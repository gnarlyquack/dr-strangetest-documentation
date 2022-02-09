<?php

function produce_output(): void
{
    echo 'Expected output';
    trigger_error('Did I err?');
}


function produce_more_output(): void
{
    echo 'More expected output';
    trigger_error('Did I err again?');
}
