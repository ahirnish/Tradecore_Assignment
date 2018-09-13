# API Overview

- [Authorization](#authorization)
- [Schema](#schema)
- [Pagination](#pagination)
- [API Endpoints](#api-endpoints)
- [Errors](#errors)


## Authorization

The Tradecore Assignment API allows, and in some cases requires, requests to include an access token to authorize elevated client privileges. Pass the access token via the standard `Authorization` HTTP header as type `Bearer`.

    curl -H "Authorization: Bearer <access_token>" https://localhost:8000/api/<endpoint>/

## Schema

- In production all API access should be over HTTPS. All data is sent and received as `JSON`.
- Response body either contains `message` parameter stating the error or warning or serialized data in case of successful operation.

       {
          "message": "can not authenticate with the given credentials or account is closed"
       }
       
       {
          "id": 1,
          "username": "username_jOOP4uzMpv",
          "email": "parth@hiration.com",
          "first_name": "first_name_XngMymiB0l",
          "last_name": "last_name_0uUS7neVEf",
          "profile": {
              "location": null,
              "bio": null,
              "site": null,
              "timezone": null,
              "utc_offset": null,
              "company_name": "Hiration",
              "company_role": null,
              "facebook_handle": null,
              "twitter_handle": null,
              "github_handle": null,
              "linkedin_handle": null,
              "googleplus_handle": null
          }
       }
       
## Pagination

GET endpoints support pagination. Responses from such endpoints contain `count`, `next` and `previous` in the response body other than actual data:
 
      {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [
              {
                  "id": 1,
                  "username": "username_jOOP4uzMpv",
                  "email": "parth@hiration.com",
                  "first_name": "first_name_XngMymiB0l",
                  "last_name": "last_name_0uUS7neVEf",
                  "profile": {
                      "location": null,
                      "bio": null,
                      "site": null,
                      "timezone": null,
                      "utc_offset": null,
                      "company_name": "Hiration",
                      "company_role": null,
                      "facebook_handle": null,
                      "twitter_handle": null,
                      "github_handle": null,
                      "linkedin_handle": null,
                      "googleplus_handle": null
                  }
              }
          ]
      }

To paginate a response, the following parameters should be provided:

- `page` - Page number of the result set.

        Example:
        curl -H "Authorization: Bearer <access_token>" https://localhost:8000/api/user/all/?page=2


## API Endpoints

#### 1. User: list of users registered:
>       GET api/user/all/              
                
                
#### 2. User: data of one particular user:
>       GET api/user/<int:user_id>/
>       PUT api/user/<int:user_id>/
>       DELETE api/user/<int:user_id>/

        
#### 3. Post: create post authored by user:
>       POST api/post/


#### 4. Post: list all posts by all users:
>       GET api/post/all/


#### 5. Post: list all posts by one user:
>       GET api/post/all/<username>/


#### 6. Post: data of one particular post:
>       GET api/post/<int:post_id>/
>       PUT api/post/<int:post_id>/
>       DELETE api/post/<int:post_id>/


#### 7. Preference: list all preferences on all posts by all users:
>       GET api/preference/all/


#### 8. Preference: data of one particular preference on a given post:
>       GET api/preference/<int:post_id>/
>       POST api/preference/<int:post_id>/
>       PUT api/preference/<int:post_id>/
>       DELETE api/preference/<int:post_id>/


## Errors

There are some common errors a client may receive when calling the API.

1. `username` and/or `password` not provided while login.
2. `username` and/or `password` are wrong while login.
3. `username` and/or `password` and/or `email` not provided while sign-up.
4. `email` is not a valid email address while sign-up.
5. `username` already exists while sign-up.
6. `user_id`, `post_id`, `username` or `preference` does not exist while trying to do fetch/update/delete operations.
7. User not logged in to perform certain actions.
8. User not authorized to perform certain actions.
9. Invalid value of `preference` provided.
10. User can't like/dislike his/her own post.
11. User can't like/dislike the same post again.
