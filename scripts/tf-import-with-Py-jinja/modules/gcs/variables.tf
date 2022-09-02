variable "name" {
  type        = string
  description = "Display name for the Bucket"
}

variable "location" {
  type        = string
  description = "Location of the Bucket"
}

variable "force_destroy" {
  type        = string
  description = "(Optional, Default: false) When deleting a bucket, this boolean option will delete all contained objects. If you try to delete a bucket that contains objects, Terraform will fail that run."
  default     = ""
}

variable "storage_class" {
  type        = string
  description = "(Optional, Default: 'STANDARD') The Storage Class of the new bucket. Supported values include: STANDARD, MULTI_REGIONAL, REGIONAL, NEARLINE, COLDLINE, ARCHIVE."
}

variable "version" {
  type        = string
  description = "The bucket's Versioning configuration."
  default     = true
}

variable "uniform_bucket_level_access" {
  type        = string
  description = "Enables Uniform bucket-level access access to a bucket."
  default     = true
}
