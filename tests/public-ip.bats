load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test public-ip command for success output" {
    run public-ip
    assert_success
}
