variable "AWS_ACCESS_KEY_ID" {
  type = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
  sensitive = true
}

variable "policies_configurations" {
  type = list(object({
    name = string
    statements = list(object({
      restriction_name = string
      actions = list(string)
      resources = list(string)
      conditions = list(object({
        test = string
        variable = string
        values = list(string)
      }))
    }))
  }))
}

variable "users_configurations" {
  type = list(object({
    username = string
  }))
}

variable "user_policy_attachments" {
  type = list(object({
    key = number
    username = string
    policy_name = string
  }))
}