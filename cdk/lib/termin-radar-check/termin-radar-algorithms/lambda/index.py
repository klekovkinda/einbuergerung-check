from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()


@logger.inject_lambda_context
@tracer.capture_lambda_handler
def service_berlin_de(event, context):
    logger.debug("Received event", extra={"event": event})
    service_name = event.get("service_name")
    service_page_content_s3_bucket = event.get("service_page_content_s3_bucket")
    service_page_content_s3_key = event.get("service_page_content_s3_key")
    return {"result": "OK", }
