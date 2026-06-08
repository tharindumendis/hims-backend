# hims-backend


## Testing Scripts

### Integration Tests

```bash
$env:TEST_MODE="integration"; backend\.venv\Scripts\pytest backend/tests/ -v
```


### Unit Tests

```bash
$env:TEST_MODE="unit"; backend\.venv\Scripts\pytest backend/tests/ -v
```