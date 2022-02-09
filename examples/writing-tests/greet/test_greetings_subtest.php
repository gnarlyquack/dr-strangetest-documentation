<?php

use example\greet\{MorningGreet, AfternoonGreet, EveningGreet, NightGreet};

function test_greetings_subtest(strangetest\Context $context)
{
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as $greeting)
    {
        $context->subtest(
            function () use ($greeting)
            {
                [$greeter, $expected] = $greeting;
                strangetest\assert_identical($expected, $greeter->greet());
            }
        );
    }
}
