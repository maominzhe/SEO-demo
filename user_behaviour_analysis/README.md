

## Tables

### 1. User Attributes
| Field       | Description                | Remarks                             |
|-------------|----------------------------|-------------------------------------|
| user_id     | User ID                    |                                     |
| age         | Age                        | -1 means unknown                    |
| sex         | Gender                     | 0: unknown, 1: male, 2: female      |
| user_lv_cd  | User level code            | Defines the level of user activity, the higher the more active |
| user_reg_tm | User registration time     | Actual registration time            |

### 2. Product Attributes

| Field  | Description     | Remarks             |
|--------|-----------------|---------------------|
| sku_id | SKU Number      | Unique identifier   |
| a1     | Type 1          | Category, -1 unknown|
| a2     | Type 2          | Category, -1 unknown|
| a3     | Type 3          | Category, -1 unknown|
| cate   | Category ID     | Unique identifier   |
| brand  | Brand ID        | Unique identifier   |



### 3. Comment Information

| Field              | Description                 | Remarks                           |
|--------------------|-----------------------------|-----------------------------------|
| dt                 | Date of record              | Date when the data was recorded   |
| sku_id             | Product SKU                 | Unique identifier for products    |
| comment_num        | Number of comments interval | 0: no comments, 1: 1 comment, 2: 2-10 comments, 3: 11-50 comments, 4: over 50 comments |
| has_bad_comment    | Has negative review         | 0: No, 1: Yes                     |
| bad_comment_rate   | Negative review rate        | Percentage of negative reviews    |




### 4. Transaction Attributes

| Field    | Description                | Remarks                                                    |
|----------|----------------------------|------------------------------------------------------------|
| user_id  | User ID                    | Unique identifier for users                                |
| sku_id   | Product SKU                | Unique identifier for products                             |
| time     | Action Time                | Timestamp of the user action                               |
| model_id | Model ID                   | Model code, applicable for specific actions or products    |
| type     | Type of Action             | 1: Click, 2: Add to cart, 3: Remove from cart, 4: Purchase, 5: Add to favorites, 6: Content click |
| cate     | Category ID                | Unique identifier for product category                     |
| brand    | Brand ID                   | Unique identifier for brand                                |
