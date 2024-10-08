// SPDX-License-Identifier: MIT
pragma solidity >= 0.4.16 < 0.9.0;

contract ElectricityMeterReading

{


    struct MeterReading{
        string uid; 
        uint256 mtr_reading;
        address addr;  
    }
    

    mapping(address => MeterReading[]) private _meterReadings;

    function getMeterReadings() public view returns (MeterReading[] memory){
        return _meterReadings[msg.sender];
    }

    function getSpecificMeterReading(string memory uidValue) public view returns (MeterReading memory) {
        uint length = _meterReadings[msg.sender].length;

        for (uint i = 0; i < length; i++) {
            if (keccak256(abi.encodePacked(_meterReadings[msg.sender][i].uid)) == keccak256(abi.encodePacked(uidValue))) {
                return _meterReadings[msg.sender][i];
            }
        }
        revert("Meter reading not found");
    }

    function storeMeterReading(string memory uid, uint mtr_reading) public returns (string memory){
        MeterReading memory reading = MeterReading({uid: uid, mtr_reading: mtr_reading, addr: msg.sender });
        _meterReadings[msg.sender].push(reading);
        return uid; 
    }

}