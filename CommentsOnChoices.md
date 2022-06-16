# Comments on design choices

- I needed to get a github action that would upload to my S3 bucket. I did not want to create a new user and provide credentials. So instead:
  - Set up github as an identity provider with AWS
  - Create a role that can write to my bucket
  - Allow github actions to assume this role when triggered for my particular repository (hopefully?)
