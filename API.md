# Sayori API Routes Documentation

## `/generate`
### **Supported Methods:** `GET`, `POST`

### **Parameters**
 - `poem` (string) (required) - Text to generate an image for.
 - `font` (string) (optional) - Font to use for the poem. Will also pick a corresponding background at times. Unsupported fonts will cause an error.

Parameters can either be sent as a query string (`?poem=foobar`), or as a JSON body, with the latter taking precedence.

#### **Supported Fonts**
 - `m1` - Monika
 - `s1` - Sayori
 - `n1` - Natsuki
 - `y1` - Yuri (Normal)
 - `y2` - Yuri (Fast)
 - `y3` - Yuri (Obsessed)

### **Responses**
#### **Content-Type: application/json**
A client-side error was made, and the server was unable to generate an image as a result of this.  
Response body looks something like:
```json
{
    "error": "No body or query string.",
    "code": 0
}
```

##### **Code 0**
No body or query string was given to the API.

##### **Code 1**
The field `poem` is missing.

##### **Code 2**
The field `poem` is not a string.

##### **Code 3**
The field `poem` is empty.

##### **Code 4**
The value of the field `font` is an unsupported font. Check [here](#supported-fonts) for supported fonts.

#### **Content-Type: image/png**
The image was successfully generated, and is provided as the response's body.