<?php

namespace example;

class Database
{
    private $records = [];
    private $id = 0;

    public function createDatabase()
    {
    }

    public function deleteDatabase()
    {
    }

    public function loadTestData()
    {
    }

    public function clearTestData()
    {
    }

    public function reset()
    {
        $this->records = [];
        $this->id = 0;
    }

    public function insertRecord($record)
    {
        $this->records[$this->id] = $record;
        return $this->id++;
    }

    public function deleteRecord($id)
    {
        unset($this->records[$id]);
    }

    public function records()
    {
        return $this->records;
    }
}


class PaymentProcessor
{
    public function setTestMode()
    {
    }
}


class OrderManager
{
    private $db;
    private $pp;
    private $wasPlaced = false;

    public function __construct(Database $db, PaymentProcessor $pp)
    {
        $this->db = $db;
        $this->pp = $pp;
    }

    public function placeOrder()
    {
        if (
            !($this->db instanceof DatabaseX)
            || !($this->pp instanceof PaymentProcessorB))
        {
            $this->wasPlaced = true;
        }
    }

    public function wasPlaced()
    {
        return $this->wasPlaced;
    }
}


class DatabaseX extends Database
{
}

class DatabaseY extends Database
{
}

class PaymentProcessorA extends PaymentProcessor
{
}

class PaymentProcessorB extends PaymentProcessor
{
}
