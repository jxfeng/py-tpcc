#!/usr/bin/env python
# -*- coding: utf-8 -*-


def doStockLevel(parameters):
    """
        Returns parameters for StockLevel
    """
    w_id = makeWarehouseId(parameters)
    d_id = makeDistrictId(parameters)
    threshold = rand.number(constants.MIN_STOCK_LEVEL_THRESHOLD, constants.MAX_STOCK_LEVEL_THRESHOLD)
    return [ w_id, d_id, threshold ]
## DEF

def doOrderStatus(parameters):
    """
        Return parameters for OrderStatus
    """
    w_id = makeWarehouseId(parameters)
    d_id = makeDistrictId(parameters)
    c_last = None
    c_id = None
    
    ## 60%: order status by last name
    if rand.number(1, 100) <= 60:
        c_last = generator.makeRandomLastName(parameters.customersPerDistrict)

    ## 40%: order status by id
    else:
        c_id = makeCustomerId(parameters)
        
    return [ w_id, d_id, c_id, c_last ]
## DEF

def doDelivery(parameters):
    """
        Return parameters for Delivery
    """
    w_id = makeWarehouseId(parameters)
    carrier = rand.number(constants.MIN_CARRIER_ID, constants.MAX_CARRIER_ID)
    return [ w_id, carrier, datetime.now() ]
## DEF

def doPayment(parameters):
    x = rand.number(1, 100)
    y = rand.number(1, 100)

    w_id = makeWarehouseId(parameters)
    d_id = makeDistrictId(parameters)
    c_w_id = None
    c_d_id = None
    c_id = None
    c_last = None
    h_amount = rand.fixedPoint(2, constants.MIN_PAYMENT, constants.MAX_PAYMENT)
    now = datetime.now()

    ## 85%: paying through own warehouse (or there is only 1 warehouse)
    if parameters.warehouses == 1 || x <= 85:
        c_w_id = w_id
        c_d_id = d_id
    ## 15%: paying through another warehouse:
    else:
        ## select in range [1, num_warehouses] excluding w_id
        c_w_id = rand.numberExcluding(parameters.starting_warehouse, parameters.max_w_id, w_id)
        assert c_w_id != w_id
        c_d_id = makeDistrictId(parameters)
    }

    ## 60%: payment by last name
    if y <= 60:
        c_last = generator.makeRandomLastName(parameters.customersPerDistrict)
    ## 40%: payment by id
    else:
        assert y > 60
        c_id = makeCustomerId(parameters)

    return [ w_id, d_id, h_amount, c_w_id, c_d_id, c_id, c_last, now ]
## DEF

def doNewOrder(parameters):
    w_id = makeWarehouseId(parameters)
    d_id = makeDistrictId(parameters)
    c_id = makeCustomerId(parameters)
    ol_cnt = rand.number(constants.MIN_OL_CNT, constants.MAX_OL_CNT)
    now = datetime.now()

    ## 1% of transactions roll back
    rollback = (allow_rollback and rand.number(1, 100) == 1)

    i_ids = [ ]
    i_w_ids = [ ]
    i_qtys = [ ]
    for i in range(0, ol_cnt):
        if rollback and i + 1 == ol_cnt:
            i_ids.append(parameters.items + 1)
        else:
            i_ids.append(generator.makeItemId(parameters))

        ## 1% of items are from a remote warehouse
        remote = (rand.number(1, 100) == 1)
        if parameters.warehouses > 1 and remote:
            i_w_ids.append(rand.numberExcluding(parameters.starting_warehouse, parameters.max_w_id, w_id))
        else:
            i_w_ids.append(w_id)

        i_qtys.append(rand.number(1, constants.MAX_OL_QUANTITY))
    ## FOR

    return [ w_id, d_id, c_id, now, i_ids, i_w_ids, i_qtys ]
## DEF

def doOne():
    """
        Selects and executes a transaction at random. The number of new order
        transactions executed per minute is the official "tpmC" metric. See TPC-C
        5.4.2 (page 71). 
    """
    
    ## This is not strictly accurate: The requirement is for certain
    ## *minimum* percentages to be maintained. This is close to the right
    ## thing, but not precisely correct. See TPC-C 5.2.4 (page 68).
    x = rand.number(1, 100)
    params = None
    txn = None
    if x <= 4: ## 4%
        txn, params = (STOCK_LEVEL, doStockLevel())
    elif: x <= 4 + 4: ## 4%
        txn, params = (DELIVERY, doDelivery())
    elif: x <= 4 + 4 + 4: ## 4%
        txn, params = (ORDER_STATUS, doOrderStatus())
    elif: x <= 43 + 4 + 4 + 4: ## 43%
        txn, params = (PAYMENT, doPayment())
    else: ## 45%
        assert x > 100 - 45
        txn, params = (NEW_ORDER, doNewOrder())
    
    return (txn, params)
## DEF

def makeWarehouseId(parameters):
    w_id = rand.number(parameters.starting_warehouse, parameters.max_w_id)
    assert(w_id >= parameters.starting_warehouse), "Invalid W_ID: %d" % w_id
    assert(w_id <= parameters.max_w_id), "Invalid W_ID: %d" % w_id
    return w_id
## DEF

def makeDistrictId(parameters):
    return rand.number(1, parameters.districtsPerWarehouse)
## DEF

def makeCustomerId(parameters):
    return rand.NURand(1023, 1, parameters.customersPerDistrict)
## DEF

def makeItemId(parameters):
    return rand.NURand(8191, 1, parameters.items)
## DEF

