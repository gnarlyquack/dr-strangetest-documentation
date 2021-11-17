<?php


const CODE = <<<'CODE'
<?php

function foo(): array
{
}
CODE;


$tokens = token_get_all(CODE);
print_r($tokens);
