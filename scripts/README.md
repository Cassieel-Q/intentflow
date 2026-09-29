# Scripts

Small repository-maintenance scripts live here.

## check-temporary-test-artifacts.sh

Run this before commit or delivery to find temporary TDD and probe markers:

```sh
./scripts/check-temporary-test-artifacts.sh .
```

If it finds `TEMP_TDD`, `SCRATCH_TEST`, `TEMP_TEST`, `临时测试`, or
`探针测试`, remove the temporary artifact or promote it to a retained test
and remove the temporary marker.
