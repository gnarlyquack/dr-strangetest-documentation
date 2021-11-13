<?php

use example\greet\{MorningGreet, AfternoonGreet, EveningGreet, NightGreet};

function test_greetings()
{
    $greetings = [
        [new MorningGreet, 'Good morning, world!'],
        [new AfternoonGreet, 'Good afternoon, world!'],
        [new EveningGreet, 'Good evening, world!'],
        [new NightGreet, 'Good night, world!'],
    ];

    foreach ($greetings as [$greeter, $expected]) {
        strangetest\assert_identical($expected, $greeter->greet());
    }
}
