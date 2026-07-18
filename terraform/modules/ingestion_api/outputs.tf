output "api_endpoint" {
  description = "Base URL for the event ingestion API."
  value       = aws_apigatewayv2_api.this.api_endpoint
}

output "events_endpoint" {
  description = "Full URL for posting experiment events."
  value       = "${aws_apigatewayv2_api.this.api_endpoint}/events"
}

output "lambda_function_name" {
  description = "Name of the ingestion Lambda function."
  value       = aws_lambda_function.ingest.function_name
}