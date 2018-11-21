
-[ ] Configure postgres as database.
-[ ] Research designs for site.
-[ ] Research using s3 for storage backend.
-[ ] Create longterm google account for gmail auth.
-[ ] Expose an authenticated API for service
    -[ ] Django REST API
        - https://wsvincent.com/django-rest-framework-user-authentication-tutorial/
    -[ ] Configure behind AWS API Gateway
-[x] Set up production network
    -[x] configure pub/private subnets
    -[x] create database
    -[x] create load balancer
    -[x] configure container cluster
    -[x] configure service container
-[ ] set up bastion host
-[ ] [configure application deployment](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-basics.html)
    -[ ] configure/build docker container for app
    -[ ] push docker container to ecr
-[ ] Change sort media to write metadata to db
-[ ] scope storage of media in S3 to a user account
-[ ] design website


Sharing concepts
* my photos: show all photos by me
* my groups: show all photos shared with me
    * my family: show all photos shared by this group with me
