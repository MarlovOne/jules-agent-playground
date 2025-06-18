# jules-agent-playground

1. RESTful API for Internal Data Retrieval and Aggregation
   
**Description:**
A backend service that provides a unified RESTful API to aggregate data from two internal data sources (relational databases and CSV files). The API enables retrieval of business-critical information, such as client details, product inventory, or sales figures, in a standardized JSON format.
Technical Objectives & Scope: 
Implement a RESTful service using the programming language and framework most familiar to the development team, such as .NET, Java, Python (Flask/FastAPI), Node.js (Express) or anything else.
Integrate database queries (PostgreSQL) and a flat file data source.
Expose the following endpoints: `/clients`, `/products`, and `/sales`. These endpoints should return JSON payloads without any filtering, providing either a list of records or a single record. `/sales` should include the client and product details in the response.
Use Swagger/OpenAPI for API documentation.

**Business Value and Reasoning:**
Consolidates dispersed data sources into a single access layer.
Provides immediate value for internal teams who need consistent data endpoints.
Swagger documentation simplifies both onboarding and integration into downstream systems.
