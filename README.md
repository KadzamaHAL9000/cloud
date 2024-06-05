# Local development

1. Following environment variables must be set:

```
FIREBASE_PRIVATE_KEY_ID
FIREBASE_PRIVATE_KEY
FIREBASE_CLIENT_ID
OPENSCAD_EXECUTABLE
```

You can get Firebase credentials in service account credentials JSON.

2. Install dependencies

```shell
make install
```

3. Run tests

```shell
make test
```

4. Run development server
```shell
make run
```
