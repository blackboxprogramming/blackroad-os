from __future__ import annotations

import re
from typing import Any


class MiniYAMLError(ValueError):
    pass


def _split_top_level(value: str, sep: str = ",") -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote: str | None = None
    for ch in value:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch in "[{(":
            depth += 1
            buf.append(ch)
        elif ch in "]})":
            depth -= 1
            buf.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    if buf or value.strip():
        parts.append("".join(buf).strip())
    return parts


def _split_key_value(value: str) -> tuple[str, str]:
    depth = 0
    quote: str | None = None
    for index, ch in enumerate(value):
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[{(":
            depth += 1
        elif ch in "]})":
            depth -= 1
        elif ch == ":" and depth == 0:
            return value[:index].strip(), value[index + 1 :].strip()
    raise MiniYAMLError(f"expected key:value pair: {value!r}")


def _scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    lower = value.lower()
    if lower == "null" or value == "~":
        return None
    if lower == "true":
        return True
    if lower == "false":
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [_scalar(part) for part in _split_top_level(inner)]
    if value.startswith("{") and value.endswith("}"):
        inner = value[1:-1].strip()
        result: dict[str, Any] = {}
        if not inner:
            return result
        for part in _split_top_level(inner):
            key, item = _split_key_value(part)
            result[key] = _scalar(item)
        return result
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_simple_yaml(text: str) -> Any:
    """Parse the deliberately small YAML subset used by Canon/Network.

    This keeps road-network dependency-free. It supports indentation-based maps,
    lists, inline lists/maps, booleans, nulls, integers, and plain strings. It is
    intentionally not a general YAML implementation.
    """

    tokens: list[tuple[int, str, int]] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        prefix = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in prefix:
            raise MiniYAMLError(f"tabs are not supported at line {lineno}")
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append((indent, raw.strip(), lineno))

    if not tokens:
        return {}

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        if index >= len(tokens):
            return None, index
        if tokens[index][0] != indent:
            raise MiniYAMLError(f"unexpected indentation at line {tokens[index][2]}")

        if tokens[index][1].startswith("- "):
            result_list: list[Any] = []
            while index < len(tokens):
                current_indent, content, lineno = tokens[index]
                if current_indent < indent:
                    break
                if current_indent > indent:
                    raise MiniYAMLError(f"unexpected list indentation at line {lineno}")
                if not content.startswith("- "):
                    break

                body = content[2:].strip()
                if not body:
                    if index + 1 >= len(tokens) or tokens[index + 1][0] <= indent:
                        result_list.append(None)
                        index += 1
                        continue
                    value, index = parse_block(index + 1, tokens[index + 1][0])
                    result_list.append(value)
                    continue

                if body.startswith("{"):
                    result_list.append(_scalar(body))
                    index += 1
                    continue

                if ":" in body:
                    key, value_text = _split_key_value(body)
                    item: dict[str, Any] = {key: _scalar(value_text) if value_text else None}
                    index += 1
                    if index < len(tokens) and tokens[index][0] > indent:
                        child_indent = tokens[index][0]
                        while index < len(tokens):
                            nested_indent, nested_content, nested_lineno = tokens[index]
                            if nested_indent <= indent:
                                break
                            if nested_indent != child_indent or nested_content.startswith("- "):
                                raise MiniYAMLError(
                                    f"unsupported nested list-item structure at line {nested_lineno}"
                                )
                            nested_key, nested_value_text = _split_key_value(nested_content)
                            if nested_value_text:
                                item[nested_key] = _scalar(nested_value_text)
                                index += 1
                            elif index + 1 >= len(tokens) or tokens[index + 1][0] <= nested_indent:
                                item[nested_key] = None
                                index += 1
                            else:
                                nested, next_index = parse_block(index + 1, tokens[index + 1][0])
                                item[nested_key] = nested
                                index = next_index
                    result_list.append(item)
                    continue

                result_list.append(_scalar(body))
                index += 1
            return result_list, index

        result_map: dict[str, Any] = {}
        while index < len(tokens):
            current_indent, content, lineno = tokens[index]
            if current_indent < indent:
                break
            if current_indent > indent:
                raise MiniYAMLError(f"unexpected mapping indentation at line {lineno}")
            if content.startswith("- "):
                break

            key, value_text = _split_key_value(content)
            if key in result_map:
                raise MiniYAMLError(f"duplicate key {key!r} at line {lineno}")
            if value_text:
                result_map[key] = _scalar(value_text)
                index += 1
            elif index + 1 >= len(tokens) or tokens[index + 1][0] <= indent:
                result_map[key] = None
                index += 1
            else:
                nested, next_index = parse_block(index + 1, tokens[index + 1][0])
                result_map[key] = nested
                index = next_index
        return result_map, index

    root, final_index = parse_block(0, tokens[0][0])
    if final_index != len(tokens):
        raise MiniYAMLError(f"trailing content at line {tokens[final_index][2]}")
    return root
