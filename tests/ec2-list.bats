load "${BLIBS}/bats-support/load.bash"
load "${BLIBS}/bats-assert/load.bash"

@test "Test ec2-list command for success output" {
    run ec2 list
    assert_success
}
