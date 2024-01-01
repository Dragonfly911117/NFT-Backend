create view `Profit From Transaction` as
(
SELECT T.shop_uuid,
       SUM(P.price * TPL.quantity * COALESCE((C.discount / 100), 1)) AS profit
FROM Transaction T
         LEFT JOIN TransactionProductLog TPL ON T.transaction_uuid = TPL.transaction_uuid
         LEFT JOIN Product P ON TPL.product_uuid = P.product_uuid
         LEFT JOIN Coupon C ON T.coupon_uuid = C.coupon_uuid
GROUP BY T.transaction_uuid
    );

create view `Shop Profit` as
(
SELECT S.shop_uuid                  AS `Shop ID`,
       S.name                       AS `Shop Name`,
       COALESCE(SUM(PFT.profit), 0) AS `Profit`
FROM Shop S
         LEFT JOIN `Profit From Transaction` PFT
                   ON S.shop_uuid = PFT.shop_uuid
GROUP BY S.shop_uuid
    );
