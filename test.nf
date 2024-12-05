#!/usr/bin/env nextflow

/*
 * Use echo to print 'Hello World!' to standard out
 */
process sayHello {

    output:
        stdout

    script:
    """
    echo 'Hello World!'
    """
}
process sayHello1 {
    publishDir 'results', mode: 'copy'
    input:
        val greeting

    output:
        path "output.txt"
}
workflow {

    // emit a greeting
    sayHello()
    sayHello1("HELLO")
}
process convertToUpper {

    publishDir 'results', mode: 'copy'

    input:
        path input_file

    output:
        path "UPPER-${input_file}"

    script:
    """
    cat '$input_file' | tr '[a-z]' '[A-Z]' > UPPER-${input_file}
    """
}


