#!/usr/bin/perl -w

use ElixirFM;
use ElixirFM::Exec;
use Encode::Arabic ':modes';
use Encode::Arabic::ArabTeX ':simple';


use Data::Dumper;
use JSON;

$s = "";
for my $root_id (419 .. 420)
{

$r = ElixirFM::Exec::elixir "lookup", "($root_id,[])";
@lines = split("\n", $r);
for my $i (0 .. $#lines)
{
    @cols = split("\t", $lines[$i]);
    $cols[4] = encode "utf8", decode "arabtex", $cols[4];
    $cols[5] = encode "utf8", decode "arabtex", $cols[5];
    $lines[$i] = join("\t", @cols);
}

$s .= join("\n", @lines) . "\n";
}

@u = ElixirFM::unpretty $s;
$r = JSON->new()->allow_nonref()->encode(\@u);
print $r;
