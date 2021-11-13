<?php

namespace {
    function test_one(strangetest\Context $context)
    {
        $context->set('global function one');
    }

    function test_two(strangetest\Context $context)
    {
        $actual = $context->requires(
            'test_one',
            'Test::test_one',
            'example\test_one',
            'example\Test::test_one'
        );
        $expected = [
            'test_one' => 'global function one',
            'Test::test_one' => 'global method one',
            'example\test_one' => 'example function one',
            'example\Test::test_one' => 'example method one',
        ];
        assert($actual === $expected);
    }

    class Test
    {
        public function test_one(strangetest\Context $context)
        {
            $context->set('global method one');
        }

        public function test_two(strangetest\Context $context)
        {
            $actual = $context->requires(
                'test_one',
                '::test_one',
                'example\test_one',
                'example\Test::test_one'
            );
            $expected = [
                'test_one' => 'global method one',
                '::test_one' => 'global function one',
                'example\test_one' => 'example function one',
                'example\Test::test_one' => 'example method one',
            ];
            assert($actual === $expected);
        }
    }
}

namespace example {

    use strangetest;

    function test_one(strangetest\Context $context)
    {
        $context->set('example function one');
    }

    function test_two(strangetest\Context $context)
    {
        $actual = $context->requires(
            'test_one',
            'Test::test_one',
            '\test_one',
            '\Test::test_one'
        );
        $expected = [
            'test_one' => 'example function one',
            'Test::test_one' => 'example method one',
            '\test_one' => 'global function one',
            '\Test::test_one' => 'global method one',
        ];
        assert($actual === $expected);
    }

    class Test
    {
        public function test_one(strangetest\Context $context)
        {
            $context->set('example method one');
        }

        public function test_two(strangetest\Context $context)
        {
            $actual = $context->requires(
                'test_one',
                '::test_one',
                '\test_one',
                '\Test::test_one'
            );
            $expected = [
                'test_one' => 'example method one',
                '::test_one' => 'example function one',
                '\test_one' => 'global function one',
                '\Test::test_one' => 'global method one',
            ];
            assert($actual === $expected);
        }
    }
}
