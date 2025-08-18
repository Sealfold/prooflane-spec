# Embeddings Binary Format (embeddings.bin)

- Encoding: little-endian
- DType: float32 (MUST), float16 (MAY)
- Layout: row-major, contiguous
- Count: N vectors, each of dimension `dim` from `search/metadata.json`
- File size MUST equal `N * dim * bytes_per_element`
- No header; consumers MUST use `metadata.json` for shape
