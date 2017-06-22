load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test getmac command for success output" {
    run getmac
    assert_success
}
