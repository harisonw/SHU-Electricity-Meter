// SPDX-License-Identifier: MIT
pragma solidity >= 0.4.16 < 0.9.0;

contract ElectricityMeterReading

{

    uint public setData;
    function set(uint x) public

    {

        setData = x;

    }

    function get(

    ) public view returns (uint) {

        return setData;

    }

}