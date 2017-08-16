load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test ghi command for success output" {
    run ghi list
    assert_success
}
