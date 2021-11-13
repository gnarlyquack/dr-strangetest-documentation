<?php

namespace example\greet;


final class Hello {
    public function greet($subject = 'world') {
        return "Hello, {$subject}!";
    }
}

final class GoodBye {
    public function bid($subject = 'cruel world') {
        return "Goodbye, {$subject}!";
    }
}



final class MorningGreet {
    public function greet($subject = 'world') {
        return "Hello, {$subject}!";
    }
}


final class AfternoonGreet {
    public function greet($subject = 'world') {
        return "Hello, {$subject}!";
    }
}


final class EveningGreet {
    public function greet($subject = 'world') {
        return "Hello, {$subject}!";
    }
}


final class NightGreet {
    public function greet($subject = 'world') {
        return "Hello, {$subject}!";
    }
}
