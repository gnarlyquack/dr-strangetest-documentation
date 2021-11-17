<?php declare(strict_types=1);
// test_orders.php

namespace test\orders;

use example\Database;
use example\OrderManager;
use example\PaymentProcessor;
use function strangetest\assert_true;

function setup_file(Database $database): array
{
    $database->loadTestData();

    $processor = new PaymentProcessor();
    $processor->setTestMode();

    return [$database, $processor];
}

function teardown_file(Database $database, PaymentProcessor $_): void
{
    $database->clearTestData();
}

function setup(Database $database, PaymentProcessor $processor): array
{
    $database->reset();
    return [new OrderManager($database, $processor)];
}

function teardown(OrderManager $order): void
{
    // teardown OrderManager
}

function test(OrderManager $order): void
{
    $order->placeOrder();
    assert_true($order->wasPlaced());
}
