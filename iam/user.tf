resource "aws_iam_user" "user" {
    for_each = { for user in var.users_configurations : user.username => user }
    name     = each.value.username
}

resource "aws_iam_access_key" "iam_access_key" {
    for_each = { for user in var.users_configurations : user.username => user }
    user = aws_iam_user.user[each.value.username].name
}

resource "aws_iam_user_policy_attachment" "user_policy_attachment" {
    for_each = { for user_policy in var.user_policy_attachments : user_policy.key => user_policy }
    user       = aws_iam_user.user[each.value.username].name
    policy_arn = aws_iam_policy.ec2_policy[each.value.policy_name].arn
}

resource "aws_iam_user_login_profile" "profile" {
    for_each                = { for user in var.users_configurations : user.username => user }
    user                    = aws_iam_user.user[each.value.username].name
    password_length         = 10
    password_reset_required = false
}

output "created_users" {
    value = { for user, profile in aws_iam_user_login_profile.profile : user => profile.password }
}