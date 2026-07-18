resource "aws_glue_catalog_database" "this" {
  name        = replace("${var.name_prefix}_analytics", "-", "_")
  description = "Glue database for ExperimentLake analytics tables."
}

resource "aws_glue_catalog_table" "raw_events" {
  name          = "raw_events"
  database_name = aws_glue_catalog_database.this.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification = "json"
    typeOfData     = "file"
  }

  partition_keys {
    name = "experiment_id"
    type = "string"
  }

  partition_keys {
    name = "event_date"
    type = "string"
  }

  partition_keys {
    name = "ingest_date"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${var.raw_bucket_name}/events/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      name                  = "json-serde"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"

      parameters = {
        "ignore.malformed.json" = "true"
      }
    }

    columns {
      name = "event_id"
      type = "string"
    }

    columns {
      name = "user_id"
      type = "string"
    }

    columns {
      name = "session_id"
      type = "string"
    }

    columns {
      name = "variant"
      type = "string"
    }

    columns {
      name = "event_name"
      type = "string"
    }

    columns {
      name = "event_timestamp"
      type = "string"
    }

    columns {
      name = "device_type"
      type = "string"
    }

    columns {
      name = "country"
      type = "string"
    }

    columns {
      name = "traffic_source"
      type = "string"
    }

    columns {
      name = "plan_type"
      type = "string"
    }

    columns {
      name = "revenue"
      type = "double"
    }

    columns {
      name = "is_duplicate"
      type = "boolean"
    }

    columns {
      name = "is_late_arriving"
      type = "boolean"
    }

    columns {
      name = "_ingested_at"
      type = "string"
    }
  }
}