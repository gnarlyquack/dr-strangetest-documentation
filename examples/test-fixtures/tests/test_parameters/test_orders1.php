<?php declare(strict_types=1);
// test_orders.php

namespace test1\orders;

use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use function strangetest\assert_true;

function setup_file(): array
{
    $processor = new PaymentProcessor();
    $processor->setTestMode();
    return [$processor];
}

function setup(Database $database, PaymentProcessor $processor): array
{
    return [new OrderManager($database, $processor)];
}

function test(OrderManager $order): void
{
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
