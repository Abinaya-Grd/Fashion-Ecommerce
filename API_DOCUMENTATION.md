# Fashion Ecommerce Backend API Documentation

## Base URL

Local:
http://127.0.0.1:8000

## Authentication

All protected APIs need:

Authorization: Bearer <access_token>

---

## Accounts APIs

### Register
POST /api/accounts/register

Body:
{
  "username": "Abi",
  "email": "abi@gmail.com",
  "phone": "9876543210",
  "password": "Abi@123"
}

### Login
POST /api/accounts/login

Body:
{
  "email": "abi@gmail.com",
  "password": "Abi@123"
}

### Profile
GET /api/accounts/profile

### Update Profile
PUT /api/accounts/profile

### Change Password
POST /api/accounts/change-password

### Forgot Password
POST /api/accounts/forgot-password

### Reset Password
POST /api/accounts/reset-password

---

# Products APIs

### Get All Products
GET /api/products

### Get Product By Id
GET /api/products/{id}

### Create Product (Admin)
POST /api/products

### Update Product
PUT /api/products/{id}

### Delete Product
DELETE /api/products/{id}

### Latest Products
GET /api/products/latest

### Featured Products
GET /api/products/featured

### Trending Products
GET /api/products/trending

### Best Sellers
GET /api/products/best-sellers

### Recommended Products
GET /api/products/recommended

### Related Products
GET /api/products/{id}/related

### Search Products
GET /api/products?search=shirt

### Filter Products
GET /api/products?category=1
GET /api/products?brand=1
GET /api/products?min_price=500&max_price=2000

### Pagination
GET /api/products?page=1&page_size=10

---

# Cart APIs

### Get Cart
GET /api/cart

### Add To Cart
POST /api/cart/add

Body:
{
  "product": 1,
  "variant": 1,
  "quantity": 2
}

### Update Cart Item
PUT /api/cart/update/{cartitemid}

Body:
{
  "quantity": 3
}

### Remove Cart Item
DELETE /api/cart/remove/{cartitemid}

### Clear Cart
DELETE /api/cart/clear


# Wishlist APIs

### Get Wishlist
GET /api/wishlist

### Add To Wishlist
POST /api/wishlist/add

Body:
{
  "product": 1,
  "variant": 1
}

### Remove From Wishlist
DELETE /api/wishlist/remove/{wishlistid}

---

# Coupons APIs

### Get All Coupons
GET /api/coupons

### Get Coupon By Id
GET /api/coupons/{id}

### Create Coupon (Admin)
POST /api/coupons

Body:

```json
{
  "code": "WELCOME10",
  "discount_type": "percentage",
  "discount_value": 10,
  "min_order_amount": 500,
  "max_discount_amount": 100,
  "usage_limit": 100,
  "start_date": "2026-07-01",
  "end_date": "2026-07-31",
  "status": "active"
}
```

### Update Coupon
PUT /api/coupons/{id}

### Delete Coupon
DELETE /api/coupons/{id}

### Validate Coupon
POST /api/coupons/validate

Body:

```json
{
  "coupon_code": "WELCOME10",
  "order_amount": 1200
}
```

---

# Cart APIs

### Get Cart
GET /api/cart

### Add To Cart
POST /api/cart/add

Body:
{
  "product": 1,
  "variant": 1,
  "quantity": 2
}

### Update Cart Item
PUT /api/cart/update/{cartitemid}

Body:
{
  "quantity": 3
}

### Remove Cart Item
DELETE /api/cart/remove/{cartitemid}

### Clear Cart
DELETE /api/cart/clear


---

# Wishlist APIs

### Get Wishlist
GET /api/wishlist

### Add To Wishlist
POST /api/wishlist/add

Body:
{
  "product": 1,
  "variant": 1
}

### Remove From Wishlist
DELETE /api/wishlist/remove/{wishlistid}

---

# Coupons APIs

### Get Coupons
GET /api/coupons

### Apply Coupon
POST /api/coupons/apply

Body:
{
  "coupon_code": "WELCOME10",
  "cart_total": 2000
}


---

# Orders APIs

### Create Order From Cart
POST /api/orders/create

Body:
{
  "address_id": 1,
  "coupon_code": "WELCOME10"
}

### Get Orders
GET /api/orders

### Get Order By Id
GET /api/orders/{id}

### Cancel Order
PUT /api/orders/{id}/cancel

### Update Order Status
PUT /api/orders/{id}/status

Body:
{
  "order_status": "confirmed"
}

### Track Order
GET /api/orders/{id}/track

### Order Summary
GET /api/orders/summary

---

# Payments APIs

### Create Razorpay Order

POST /api/payments/create-razorpay-order

Body

```json
{
    "order_id": 1
}
```

---

### Verify Razorpay Payment

POST /api/payments/verify-razorpay-payment

Body

```json
{
    "razorpay_order_id":"order_xxxxxxxxx",
    "razorpay_payment_id":"pay_xxxxxxxxx",
    "razorpay_signature":"xxxxxxxxxx"
}
```

---

### Payment History

GET /api/payments

---

# Reviews APIs

### Get Product Reviews

GET /api/reviews/product/{productid}

---

### Add Review

POST /api/reviews

Body

```json
{
    "product":1,
    "rating":5,
    "review":"Excellent product"
}
```

---

### Update Review

PUT /api/reviews/{id}


### Delete Review

DELETE /api/reviews/{id}

---

# Returns APIs

### Create Return Request
POST /api/returns

Body:
{
  "order": 1,
  "order_item": 1,
  "reason": "Size issue"
}

### Get My Returns
GET /api/returns

### Get Return By Id
GET /api/returns/{id}

### Cancel Return
PUT /api/returns/{id}/cancel

### Approve Return
PUT /api/returns/{id}/approve

### Reject Return
PUT /api/returns/{id}/reject


---

# Notifications APIs

### Get Notifications
GET /api/notifications

### Unread Count
GET /api/notifications/unread-count

### Mark As Read
PUT /api/notifications/{id}/read

### Mark All As Read
PUT /api/notifications/read-all

### Delete Notification
DELETE /api/notifications/{id}

---

# Wallet APIs

### Get Wallet

GET /api/wallet

---

### Wallet Transactions

GET /api/wallet/transactions

---

# Reports APIs

### Dashboard Report

GET /api/reports/dashboard

---

### Sales Report

GET /api/reports/sales

---

### Product Report

GET /api/reports/products

---

### Customer Report

GET /api/reports/customers

---

# Dashboard APIs

### Admin Dashboard

GET /api/dashboard/admin

---

### Customer Dashboard

GET /api/dashboard/customer

---

# Banner APIs

### Get Active Banners

GET /api/banners/active

---

### Get Mobile Banners

GET /api/banners/mobile

---

### Get Web Banners

GET /api/banners/web

---

### Get All Banners (Admin)

GET /api/banners

---

### Create Banner

POST /api/banners

---

### Update Banner

PUT /api/banners/{id}

---

### Delete Banner

DELETE /api/banners/{id}

---

# Inventory APIs

### Get Inventory

GET /api/inventory

---

### Get Inventory By Id

GET /api/inventory/{id}

---

### Stock In

POST /api/inventory/stock-in

---

### Stock Out

POST /api/inventory/stock-out

---

### Stock Adjustment

POST /api/inventory/adjustment

---

### Low Stock

GET /api/inventory/low-stock

---

### Out Of Stock

GET /api/inventory/out-of-stock

---

### Stock History

GET /api/inventory/history/{variant_id}