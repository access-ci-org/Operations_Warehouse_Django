Design document for oAuth authentication and authorization for Information Warehouse, specifically integration badges


Design for the Authentication and Authorization for the django rest framework APIs of the Operations Information Warehouse.

The Django web front end of the Information Warehouse has already integrated CILogon to allow users to log in and see authenticated web views.  However, Django Rest Framework APIs do not use the same authentication methods as the front end.  Thus, we need to develop some custom code to integrate CILogon authentication to our DRF APIs.

This custom authentication integration takes the form of a django app “tokenauth” which provides decorators for API functions that can consume a CILogon oAuth token and provide an authentication decision based on the validity of the token and scope, and the identity of the token.

Aside from using the same oAuth provider (CILogon), this authentication check is entirely separate from the SSO login of the Django front end.  It does not integrate with the Django users table, nor the Social Accounts table used by the front end.  It makes its own calls to introspect the tokens it receives.


Everything should be authenticated using CILogon

The integration badging endpoints are top priority for authenticating.

POST endpoints will need to be authenticated AND check authorization against a table that lists ACCESS-CI identities with the resource IDs for which they are authorized to make changes.

The route will have a decorator that will confirm that the identity is authorized to call the function to make changes.
The endpoint will also need code to look at which resource IDs they’re trying to change, and make the authorization decision.

