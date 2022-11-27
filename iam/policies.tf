data "aws_iam_policy_document" "ec2_policy" {
    for_each = {for policy in var.policies_configurations : policy.name => policy}
    policy_id = each.value.name
    dynamic statement {
        for_each = each.value.statements
        content {
            actions = statement.value.actions
            resources = statement.value.resources
            dynamic condition {
                for_each = statement.value.conditions
                content {
                    test = condition.value.test
                    variable = condition.value.variable
                    values = condition.value.values
                }
            }
        }
    }
}

resource "aws_iam_policy" "ec2_policy" {
    for_each = {for policy in var.policies_configurations : policy.name => policy}
    name        = each.value.name
    policy      = data.aws_iam_policy_document.ec2_policy[each.value.name].json
}