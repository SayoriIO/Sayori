## API Documentation
The Sayori webserver API only accepts three parameters: Mainly `poem`, `font`, and `bg`.

To make a poem at the API endpoint, simply make a GET request with query parameters.


### Example query

```bash
curl -X GET  http://localhost:7270/g?poem=Hello%20world&font=y1&bg=y2 --verbose
```

## Accepted Parameters

### `poem` - Required

Poem parameter is required and must be a string datatype. Otherwise, the API will return a 400 error.

### `font` - Optional

Font parameter must be the following in string format:

- `m1` - Monika
- `n1` - Natsuki
- `s1` - Sayori
- `y1` - Yuri
- `y2` - Yuri (Fast)
- `y3` - Yuri (Obsessed)

API will ignore any other values and default to `m1`.

### `bg` - Optional

Background parameter must be the following in string format:

- `default` - Default background
- `y2` - Yuri (Fast)
- `y3` - Yuri (Obsessed)

API will ignore any other values and default to `default`.
