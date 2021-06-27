# Data Sources Proposal

## Sources 
For the Brownsville project, we have proposed a set of data sources to explore and analyze, namely _311 Service Requests from 2010 to Present_, _Complain Problems_, and _DOB Complaints Received_. 

Before comparing these datasets, we will look at a breif overview of each dataset and their Field descriptions. 

----------
### 1) 311 Service Requests from 2010 to Present
- **Agency:** 311
- **URL:** https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9
- **Description:** All 311 Service Requests from 2010 to present. This information is automatically updated daily.
- **Field descriptions:**
        - **Description:** Unique identifier of a Service Request (SR) in the open data set 
        - **Type:** `Plain Text`
    - **Created Date**
        - **Description:** Date SR was created 
        - **Type:** `Date & Time`
    - **Closed Date**
        - **Description:** Date SR was closed by responding agency 
        - **Type:** `Date & Time`
    - **Agency**
        - **Description:** Acronym of responding City Government Agency 
        - **Type:** `Plain Text`
    - **Agency Name**
        - **Description:** Full Agency name of responding City Government Agency 
        - **Type:** `Plain Text`
    - **Complaint Type**
        - **Description:** This is the first level of a hierarchy identifying the topic of the incident or condition. Complaint Type may have a corresponding Descriptor (below) or may stand alone. 
        - **Type:** `Plain Text`
    - **Descriptor**
        - **Description:** This is associated to the Complaint Type, and provides further detail on the incident or condition. Descriptor values are dependent on the Complaint Type, and are not always required in SR. 
        - **Type:** `Plain Text`
    - **Status**
        - **Description:** Describes the type of location used in the address information 
        - **Type:** `Plain Text`
    - **Due Date**
        - **Description:** Incident location zip code, provided by geo validation. 
        - **Type:** `Plain Text`
    - **Resolution Action Updated Date**
        - **Description:** House number of incident address provided by submitter. 
        - **Type:** `Plain Text`
    - **Resolution Description**
        - **Description:** Street name of incident address provided by the submitter 
        - **Type:** `Plain Text`
    - **Location Type**
        - **Description:** First Cross street based on the geo validated incident location 
        - **Type:** `Plain Text`
    - **Incident Zip**
        - **Description:** Second Cross Street based on the geo validated incident location 
        - **Type:** `Plain Text`
    - **Incident Address**
        - **Description:** First intersecting street based on geo validated incident location 
        - **Type:** `Plain Text`
    - **Street Name**
        - **Description:** Second intersecting street based on geo validated incident location 
        - **Type:** `Plain Text`
    - **Cross Street 1**
        - **Description:** Type of incident location information available. 
        - **Type:** `Plain Text`
    - **Cross Street 2**
        - **Description:** City of the incident location provided by geovalidation. 
        - **Type:** `Plain Text`
    - **Intersection Street 1**
        - **Description:** If the incident location is identified as a Landmark the name of the landmark will display here 
        - **Type:** `Plain Text`
    - **Intersection Street 2**
        - **Description:** If available, this field describes the type of city facility associated to the SR 
        - **Type:** `Plain Text`
    - **Address Type**
        - **Description:** Status of SR submitted 
        - **Type:** `Plain Text`
    - **City**
        - **Description:** Date when responding agency is expected to update the SR. This is based on the Complaint Type and internal Service Level Agreements (SLAs). 
        - **Type:** `Date & Time`
    - **Landmark**
        - **Description:** Describes the last action taken on the SR by the responding agency. May describe next or future steps. 
        - **Type:** `Plain Text`
    - **Facility Type**
        - **Description:** Date when responding agency last updated the SR. 
        - **Type:** `Date & Time`
    - **Community Board**
        - **Description:** Provided by geovalidation. 
        - **Type:** `Plain Text`
    - **BBL**
        - **Description:** Borough Block and Lot, provided by geovalidation. Parcel number to identify the location of location of buildings and properties in NYC. 
        - **Type:** `Plain Text`
    - **Borough**
        - **Description:** Provided by the submitter and confirmed by geovalidation. 
        - **Type:** `Plain Text`
    - **X Coordinate (State Plane)**
        - **Descriptio:n* Geo validated, X coordinate of the incident location.: 
        -** Typ:**: `Number`
    - **Y Coordinate (State Plane)**
        - **Descriptio:n* Geo validated, Y coordinate of the incident location.: 
        -** Typ:**: `Number`
    - **Open_Data_Channel_Type**
        - **Description:** Indicates how the SR was submitted to 311. i.e. By Phone, Online, Mobile, Other or Unknown. 
        - **Type:** `Plain Text`
    - **Latitude**
        - **Description:** If the incident location is a Parks Dept facility, the Name of the facility will appear here 
        - **Type:** `Plain Text`
    - **Longitude**
        - **Description:** The borough of incident if it is a Parks Dept facility 
        - **Type:** `Plain Text`
    - **Location**
        - **Description:** If the incident is a taxi, this field describes the type of TLC vehicle. 
        - **Type:** `Plain Text`
    - **Park Facility Name**
        - **Description:** If the incident is identified as a taxi, this field will display the borough of the taxi company. 
        - **Type:** `Plain Text`
    - **Park Borough**
        - **Description:** If the incident is identified as a taxi, this field displays the taxi pick up location 
        - **Type:** `Plain Text`
    - **Vehicle Type**
        - **Description:** If the incident is identified as a Bridge/Highway, the name will be displayed here. 
        - **Type:** `Plain Text`
    - **Taxi Company Borough**
        - **Description:** If the incident is identified as a Bridge/Highway, the direction where the issue took place would be displayed here. 
        - **Type:** `Plain Text`
    - **Taxi Pick Up Location**
        - **Description:** If the incident location was Bridge/Highway this column differentiates if the issue was on the Road or the Ramp. 
        - **Type:** `Plain Text`
    - **Bridge Highway Name**
        - **Description:** Additional information on the section of the Bridge/Highway were the incident took place. 
        - **Type:** `Plain Text`
    - **Bridge Highway Direction**
        - **Description:** Geo based Lat of the incident location: 
        - **Type:** `Number`
    - **Road Ramp**
        - **Description** Geo based Long of the incident location: 
        - **Type:** `Number`
    - **Bridge Highway Segment**
        - **Description:** Combination of the geo based lat & long of the incident location 
        - **Type:** `Location`

`Note:` This data does not present a full picture of 311 calls or service requests, in part because of operational and system complexities associated with remote call taking necessitated by the unprecedented volume 311 is handling during the Covid-19 crisis. The City is working to address this issue.


### 2) Complaint Problems
- **Agency:** Department of Housing Preservation and Development (HPD)
- **URL:** https://data.cityofnewyork.us/Housing-Development/Complaint-Problems/a2nx-4u46
- **Description:** Contains information about problems associated with complaints.
- **Field descriptions:**
    - **ProblemID**
        - **Description:** Unique identifier of this problem
        - **Type:** `Number`
    - **ComplaintID**
        - **Description:** Unique identifier of the complaint this problem is associated with
        - **Type:** `Number`
    - **UnitTypeID**
        - **Description:** Unique number to identify unit type
        - **Type:** `Number`
    - **UnitType**
        - **Description:** Type of unit where the problem was reported
        - **Type:** `Plain Text`
    - **SpaceTypeID**
        - **Description:** Unique number to identify Space type
        - **Type:** `Number`
    - **SpaceType**
        - **Description:** Type of space where the problem was reported
        - **Type:** `Plain Text`
    - **TypeID**
        - **Description:** Unique number to identify Problem Type
        - **Type:** `Number`
    - **Type**
        - **Description:** Numeric code indicating the problem type
        - **Type:** `Plain Text`
    - **MajorCategoryID**
        - **Description:** Unique number to identify Problem Major Category
        - **Type:** `Number`
    - **MajorCategory**
        - **Description:** The major category of the problem
        - **Type:** `Plain Text`
    - **MinorCategoryID**
        - **Description:** The minor category
        - **Type:** `Number`
    - **MinorCategory**
        - **Description:** The minor category
        - **Type:** `Plain Text`
    - **CodeID**
        - **Description:** Unique number to identify problem Code
        - **Type:** `Number`
    - **Code**
        - **Description:** The problem code
        - **Type:** `Plain Text`
    - **StatusID**
        - **Description:** unique number to identify problem status
        - **Type:** `Number`
    - **Status**
        - **Description:** The status of the problem
        - **Type:** `Plain Text`
    - **StatusDate**
        - **Description:** Date when the problem status was updated
        - **Type:** `Date & Time`
    - **StatusDescription**
        - **Description:** Status description
        - **Type:** `Plain Text`


### 3) DOB Complaints Received
- **Agency:** 	Department of Buildings (DOB)
- **Description:** This is the universe of complaints received by Department of Buildings (DOB). It includes complaints that come from 311 or that are entered into the system by DOB staff.
- **URL:** https://data.cityofnewyork.us/Housing-Development/DOB-Complaints-Received/eabe-havv
- **Field descriptions:**
    - **Complaint Number**
        - **Description:** Complaint number starting with 

        | Borough Code |    Borough    |
        |:------------:|:-------------:|
        |       1      |   Manhattan   |
        |       2      |     Bronx     |
        |       3      |   Brooklyn    |
        |       4      |     Queens    |
        |       5      | Staten Island |

        - **Type:** `Plain Text`
    - **Status**
        - **Description:** Status of Complaint
        - **Type:** `Plain Text`
    - **Date Entered**
        - **Description:** Date Complaint was Entered
        - **Type:** `Plain Text`
    - **House Number**
        - **Description:** House Number of Complaint
        - **Type:** `Plain Text`
    - **ZIP Code**
        - **Description:** Zip code of complaint
        - **Type:** `Plain Text`
    - **House Street**
        - **Description:** House Street of Complaint
        - **Type:** `Plain Text`
    - **BIN**
        - **Description:** Number assigned by City Planning to a specific building
        - **Type:** `Plain Text`
    - **Community Board**
        - **Description:** 3-digit identifier: Borough code = first position, last 2 = community board
        - **Type:** `Plain Text`
    - **Special District**
        - **Description:** Is Complaint in Special District
        - **Type:** `Plain Text`
    - **Complaint Category**
        - **Description:** DOB Complaint Category Codes (01-Accident Construction/Plumbing, etc.)
        - **Type:** `Plain Text`
    - **Unit**
        - **Description:** Unit dispositioning Complaint
        - **Type:** `Plain Text`
    - **Disposition Date**
        - **Description:** Date Complaint was Dispositioned
        - **Type:** `Plain Text`
    - **Disposition Code**
        - **Description:** Disposition Code of Complaint (A1-Building Violations Served, L1-Partial Stop Work Order,etc.)
        - **Type:** `Plain Text`
    - **Inspection Date**
        - **Descriptiona:** Inspection Date of Complaint
        - **Type:** `Plain Text`
    - **DOBRunDate**
        - **Description:** Date when query is run and pushed to Open Data. Could be used to differentiate report dates.
        - **Type:** `Date & Time`

<br>

<h3><center> Table containing all field names from the aforementioned datasets </center></h1>

|311 Service Requests from 2010 to Present|Complaint Problems|DOB Complaints Received|
|:-----------------------------------:|:--------------------:|:--------------------:|
| Unique Key                          | ProblemID            | Complaint Number     |
| Created Date                        | ComplaintID          | Status               |
| Closed Date                         | UnitTypeID           | Date Entered         |
| Agency                              | UnitType             | House Number         |
| Agency Name                         | SpaceTypeID          | ZIP Code             |
| Complaint Type                      | SpaceType            | House Street         |
| Descriptor                          | TypeID               | BIN                  |
| Location Type                       | Type                 | Community Board      |
| Incident Zip                        | MajorCategoryID      | Special District     |       
| Incident Address                    | MajorCategory        | Complaint Category   |         
| Street Name                         | MinorCategoryID      | Unit                 |
| Cross Street 1                      | MinorCategory        | Disposition Date     |   
| Cross Street 2                      | CodeID               | Disposition Code     |
| Intersection Street 1               | Code                 | Inspection Date      |  
| Intersection Street 2               | StatusID             | DOBRunDate           | 
| Address Type                        | Status               |                      | 
| City                                | StatusDate           |                      |  
| Landmark                            | StatusDescription    |                      | 
| Facility Type                       |                      |                      |
| Status                              |                      |                      |
| Due Date                            |                      |                      |
| Resolution Description              |                      |                      |
| Resolution Action Updated Date      |                      |                      | 
| Community Board                     |                      |                      |
| BBL                                 |                      |                      |
| Borough                             |                      |                      |
| X Coordinate (State Plane)          |                      |                      |  
| Y Coordinate (State Plane)          |                      |                      |  
| Open Data Channel Type              |                      |                      |
| Park Facility Name                  |                      |                      |
| Park Borough                        |                      |                      | 
| Vehicle Type                        |                      |                      | 
| Taxi Company Borough                |                      |                      |
| Taxi Pick Up Location               |                      |                      |
| Bridge Highway Name                 |                      |                      |
| Bridge Highway Direction            |                      |                      |   
| Road Ramp                           |                      |                      | 
| Bridge Highway Segment              |                      |                      |
| Latitude                            |                      |                      | 
| Longitude                           |                      |                      |
| Location                            |                      |                      |
---
## Shared Fields
This section contains information of fields that share the same information or could be potentially matched according to thier values. 

1. Zip Code
    - Datasets: 
        - [311 Service Requests](#1-311-service-requests-from-2010-to-present)
            - Field name(s): `Incident Zip`
        - [DOB Complaints Received](#3-dob-complaints-received)
            - Field name(s): `ZIP Code`
2. Complaint category
    - Datasets:
        - [Complaint Problems](#2-complaint-problems)
            - Field name(s): `MajorCategory`, `MinorCategory`
        - [DOB Complaints Received](#3-dob-complaints-received)
            - Field name(s): `Complaint Category`
3. Address 
    - Datasets:
        - [311 Service Requests](#1-311-service-requests-from-2010-to-present)
            - Field name(s): `Incident Address`, `Street Name`, `Cross Street 1`, `Cross Street 2`, `Intersection Street 1`, `Intersection Street 2`, `Address Type`, `X Coordinate (State Plane)`, `Y Coordinate (State Plane)`, `Latitude`, `Longitude`, `Location`
        - [DOB Complaints Received](#3-dob-complaints-received)
            - Field name(s): `House Street`, `House Number`
4. Status and resolution
    - Datasets:
        - [311 Service Requests](#311-service-requests-from-2010-to-present)
            - Field name(s): `Status`, `Resolution Description`
        - [Complaint Problems](#2-complaint-problems)
            - Field name(s): `Status`, `StatusDescription`
        - [DOB Complaints Received](#3-dob-complaints-received)
            - Field name(s): `Status`
---
## Building Coverage
- Brownsville.csv
    - 4653 unique buildings
- [311 Service Requests](#1-311-service-requests-from-2010-to-present)
    - 6797 unique buildings
- [Complaint Problems](#2-complaint-problems)
    - TBD
- [DOB Complaints Received](#3-dob-complaints-received)
    - 7978 unique buildings
    
---
## Types of Complaints
- Brownsville.csv
    - **Major Categories:**
        - HEAT/HOT WATER
        - UNSANITARY CONDITION
        - PAINT/PLASTER
        - PLUMBING
        - DOOR/WINDOW
        - WATER LEAK
        - ELECTRIC
        - GENERAL
        - FLOORING/STAIRS
        - SAFETY
        - APPLIANCE
        - OUTSIDE BUILDING
        - ELEVATOR
        - HEATING
        - NONCONST
        - CONSTRUCTION
    - **Minor Categories:**
        - ENTIRE BUILDING
        - APARTMENT ONLY
        - PESTS
        - WALL
        - MOLD
        - CEILING
        - DOOR
        - FLOOR
        - BASIN/SINK
        - HEAVY FLOW
        - WINDOW FRAME
        - SLOW LEAK
        - WATER SUPPLY
        - BATHTUB/SHOWER
        - ELECTRIC/GAS RANGE
        - GARBAGE/RECYCLING STORAGE
        - CABINET
        - TOILET
        - OUTLET/SWITCH
        - RADIATOR
        - BELL/BUZZER/INTERCOM
        - NO LIGHTING
        - SMOKE DETECTOR
        - REFRIGERATOR
        - CARBON MONOXIDE DETECTOR
        - POWER OUTAGE
        - LIGHTING
        - COOKING GAS
        - DAMP SPOT
        - WIRING
        - DOOR FRAME
        - WINDOW GUARD BROKEN/MISSING
        - FIRE ESCAPE
        - WINDOW PANE
        - SEWAGE
        - MAILBOX
        - STAIRS
        - VENTILATION SYSTEM
        - STEAM PIPE/RISER
        - JANITOR/SUPER
        - WINDOW/FRAME
        - ROOF DOOR/HATCH
        - ROOFING
        - SIGNAGE MISSING
        - PAVEMENT
        - DOOR/FRAME
        - MAINTENANCE
        - HEAT RELATED
        - BOILER
        - SKYLIGHT
        - GUTTER/LEADER
        - SEWER
        - SPRINKLER
        - PORCH/BALCONY
        - DOOR TO DUMBWAITER
        - WATER-LEAKS
        - LOCKS
        - VERMIN
        - WINDOWS
        - BELL-BUZZER/INTERCOM
        - ELECTRIC-SUPPLY
        - CERAMIC-TILE
        - DOORS
        - RUBBISH
        - OUTLET COVER
        - MICROWAVE
        - ILLEGAL
        - HEAT-PLANT
- [311 Service Requests](#1-311-service-requests-from-2010-to-present)
    - TBD
- [Complaint Problems](#2-complaint-problems)
    - TBD
- [DOB Complaints Received](#3-dob-complaints-received)
    - TBD

---
## Date range
- Brownsville.csv
    - 12/03/2003 - 04/30/2021
- [311 Service Requests](#1-311-service-requests-from-2010-to-present)
    - 01/01/2010 - 06/25/2021
- [Complaint Problems](#2-complaint-problems)
    - 02/36/2003 - 31/05/2021
- [DOB Complaints Received](#3-dob-complaints-received)
    - 01/01/2004 - 12/21/2020