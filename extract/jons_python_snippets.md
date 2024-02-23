# Python snippets for use in wrf_extract.py

## Array of hour strings

Asking ChatGPT 3.5:

> Please show some simple python code to generate an array of hour identifiers that look like: ["00", "01", "02", ...]

```
hour_identifiers = [str(hour).zfill(2) for hour in range(24)]
print(hour_identifiers)
```

This code uses a list comprehension to iterate over numbers from 0 to 23
(inclusive) and converts each number to a string. The zfill(2) method is then
used to ensure that each string representation is padded with zeros to ensure
it's two characters long.
