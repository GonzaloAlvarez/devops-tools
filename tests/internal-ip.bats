load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test internal-ip command for success output" {
    run internal-ip
    assert_success
}
