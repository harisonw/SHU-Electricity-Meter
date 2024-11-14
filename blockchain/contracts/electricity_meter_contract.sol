// SPDX-License-Identifier: MIT
pragma solidity >= 0.4.16 < 0.9.0;

contract ElectricityMeterReading{


    struct MeterReading{
        string uid; 
        uint256 mtr_reading;    
    } 
    
    address public owner; 
    uint128 private costPerUnit;

    modifier onlyOwner(){
        require(msg.sender == owner, "Not Authorized");
        _;
    }

    event MeterReadingSubmission(address addr, MeterReading mtr);
    event GridAlert(string message); 

    mapping(address => MeterReading[]) private _meterReadings;
    mapping(address=>uint256) private _bills; 

    uint256 private cost_per_kwh = 1; 

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

    function getMeterBill() public view returns (uint256){
        return _bills[msg.sender];
    }

    function storeMeterReading(string memory uid, uint mtr_reading) public{
        MeterReading memory reading = MeterReading({uid: uid, mtr_reading: mtr_reading });
        _meterReadings[msg.sender].push(reading);
        emit MeterReadingSubmission(msg.sender, reading);
        _bills[msg.sender]+=mtr_reading*cost_per_kwh; 
    }

    function sendGridAlert(string memory _message) public{
        emit GridAlert(_message);
    }
}