load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test vtop command for success output" {
    run vtop -V
    assert_success
}
