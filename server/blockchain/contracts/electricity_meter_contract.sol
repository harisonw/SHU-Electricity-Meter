// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

contract Hero{
    address owner;
    string hero;
    constructor(string memory _hero)
    {
        owner=msg.sender;
        hero=_hero;
    }
    
    function setHero(string memory _hero)public
    {
        hero =_hero;
    }
    function getHero() public view returns(string memory)
    {
        return hero;
    }
    
}