from CvPythonExtensions import *
import datetime




gc = CyGlobalContext()
    
    
def report():
    
    terrainCoast = TerrainTypes.TERRAIN_COAST
    terrainShallowCoast = TerrainTypes.TERRAIN_SHALLOW_COAST
    final_result=[]
    player=gc.getPlayer(0)
    team = gc.getTeam(player.getTeam())
    for foundingFather in range(gc.getNumFatherInfos()):
        team.setFatherIgnore(foundingFather,False)
    europe = gc.getPlayer(player.getParent())
    game=gc.getGame()
    map=gc.getMap()
    gy=map.getGridHeight()
    gx=map.getGridWidth()
    map_to_cover_back=[]
    for my in range(gy):
        for mx in range(gx):
            mplot = map.plot(mx,my)
            if not mplot.isRevealed(0,False):
                mplot.setRevealed(0,True,True,-1)
                map_to_cover_back.append(mplot)
    turn = game.getGameTurn()
    report_id=str(game.getGameTurn())+"-"+(str(datetime.datetime.now()).replace(' ','-'))
    report_id=report_id.encode('utf-8')
    prefix=u'abmpicolireport-'+report_id
    prefixdomestic=u'abmpicolicityreport-'+report_id
    final_result.append(prefix)
    print prefixdomestic+u"\tdomestic report: "
    print prefixdomestic+u"\tcity\tdemand\tturns_left\tper_turn\tper_item\tcost\tscore"
    print prefix+u"\tgame turn report: turn=" +  CyGameTextMgr().getTimeStr(turn, False) + u"(" + str(turn)+u") : player=" + player.getName()
    line=u"team\tcity\tx\ty\tdomain\tarea\tdistance\tfrom\tvisited\ttrade_value\tgold_needed\tnative_demand\tnative_demand_buy_price\tnative_treasure\tproducts"
    print prefix+u"\t"+line
    final_result.append(line)
    units=[]
    (pUnit,iter) = player.firstUnit()
    while pUnit:
        if pUnit.getName().startswith(u"T-"):
            units.append(pUnit)
        (pUnit,iter) = player.nextUnit(iter)

    if len(units) == 0:
        line=u"abmpicoli no suitable units for cargo or scouting: Rename units of interest to start with 'T-'"
        print prefix+u"\t"+ line
        print prefix+u"\t"
        final_result.append(line)
    
    for iLoopPlayer in range(gc.getMAX_CIV_PLAYERS()):
            ePlayer = gc.getPlayer(iLoopPlayer)
            player_gold=ePlayer.getGold()
            player_gold = min(ePlayer.getGold(),ePlayer.AI_maxGoldTrade(0))
            is_myself = ePlayer.getID() == 0
            #if (player.isAlive() and player.isNative() and (gc.getTeam(player.getTeam()).isHasMet(activePlayer.getTeam()))):
            if ((ePlayer.isAlive() and ePlayer.isNative())) or is_myself:
                
                (pLoopCity, iter) = ePlayer.firstCity(False)
                while(pLoopCity):
                    if  is_myself:
                        the_domestic_yield_types=player.getDomesticDemandYieldTypes()
                        for ixDemand in range(the_domestic_yield_types.getLength()):
                            demand=the_domestic_yield_types.get(ixDemand)
                            demand_stored=pLoopCity.getYieldStored(demand)
                            demand_per_turn=pLoopCity.getYieldDemand(demand)
                            if demand_per_turn == 0:
                                continue
                            demand_turns_left=demand_stored * 1.0 / demand_per_turn
                            demand_local_price=pLoopCity.getYieldBuyPrice(demand)
                            # demands near to end or that have ended have more value than 
                            # demands for which we have supplies.
                            demand_score=(max(0,(20.0-demand_turns_left))/20.0)**2.0
                            demand_import_price=europe.getYieldSellPrice(demand)
                            demand_profit=max(0.1,(demand_local_price-demand_import_price)/demand_import_price)
                            demand_cost=demand_per_turn * demand_import_price * 20.0
                            demand_score = demand_score * demand_profit / demand_cost * 200.0
                            demand_name=gc.getYieldInfo(demand).getDescription()
                            the_line= unicode(prefixdomestic)+u"\t"+u"\t".join((
                                unicode(pLoopCity.getName()),
                                unicode(demand_name),
                                unicode(str(demand_turns_left)),
                                unicode(str(demand_per_turn)),
                                unicode(str(demand_import_price)),
                                unicode(str(demand_cost)),
                                unicode(str(demand_score))))
                            print the_line.encode('utf-8')
                                
                    value=0
                    native_demand_yield_id=pLoopCity.AI_getDesiredYield()
                    native_demand_yield=gc.getYieldInfo(native_demand_yield_id)
                    native_demand_name=u"N/A"
                    native_demand_buy_price=0
                    if native_demand_yield:
                        native_demand_name=u"".join((native_demand_yield.getDescription()))
                        native_demand_buy_price=native_demand_yield.getNativeBuyPrice()
                        native_haggling_price=native_demand_buy_price*1.5
                        amount_to_sell=player_gold / native_haggling_price
                        trade_sell_value = min(0.1,native_haggling_price - europe.getYieldBuyPrice(native_demand_yield_id))*amount_to_sell
                        value += trade_sell_value
                    cityplot = pLoopCity.plot()
                    position=(cityplot.getX(),cityplot.getY())
                    visited = pLoopCity.isScoutVisited(player.getTeam())
                    owned = ePlayer.getID()==0
                    if visited:
                        visited=u"visited"
                    else:
                        visited=u"not visited"
                    
                    domain=u"LAND"
                    if pLoopCity.isCoastal(gc.getMIN_WATER_SIZE_FOR_OCEAN()):
                        
                        domain=u"COAST.0RIVERLAKE"
                        
                        for dx in range(-1,2):
                            if domain==u"COAST.2DEEP":
                                break
                            for dy in range(-1,2):
                                dplot = map.plot(position[0]+dx,position[1]+dy)
                                if dplot:
                                    if dplot.getTerrainType() == terrainShallowCoast:
                                        domain=u"COAST.1SHALLOW"
                                        continue
                                    if dplot.getTerrainType() == terrainCoast:
                                        domain=u"COAST.2DEEP"
                                        break
                    dist=99999.9
                    nearest_unit_name=u"N/A"
                    for pUnit in units:
                        unitPlot=pUnit.plot()
                        is_in_same_plot = unitPlot.getX() == cityplot.getX() and unitPlot.getY() == cityplot.getY()
                        if is_in_same_plot or pUnit.canMoveInto(cityplot,False,False,False):
                            new_dist=99999.99
                            if is_in_same_plot:
                                new_dist=0.0
                            else:
                                new_dist=pUnit.getPathTurns(cityplot,0,False)
                            if new_dist >=0 :
                                if(new_dist < dist):
                                    nearest_unit_name=u"".join((pUnit.getName(),"(",str(pUnit.plot().getX()),",",str(pUnit.plot().getY()),")"))
                                    dist=new_dist
                    dist=dist*1.0
                    
                    gold_reserve=0
                    net_yield=0
                    products=u""
                    comma=u""
                    if owned:
                        # check for warehouse capacity and add as an extra value in the priority.
                        # code collected from WarehouseAdvisor.py
                        iMaxYield = pLoopCity.getMaxYieldCapacity()
                        iProducedYield=0
                        storage_used=0
                        for iYield in range(YieldTypes.NUM_YIELD_TYPES):
                            the_yield=gc.getYieldInfo(iYield)
                            if not the_yield.isCargo():
                                continue
                            if the_yield.isIgnoredForStorageCapacity():
                                continue
                            iProducedYield += pLoopCity.calculateActualYieldProduced(iYield)
                            storage_used += pLoopCity.getYieldStored(iYield)
                        turns_to_overflow= max(1,(iMaxYield - storage_used) / max(0.001,iProducedYield))
                        value += 1000.0/turns_to_overflow
                    the_yield_values=[]
                    for iYield in range(YieldTypes.NUM_YIELD_TYPES):
                        the_yield=gc.getYieldInfo(iYield)
                        if not the_yield.isCargo():
                            continue
                        buy_price= europe.getYieldBuyPrice(iYield)
                        sell_price = europe.getYieldSellPrice(iYield)
                        the_price_value=(buy_price+sell_price)/2.0
                        native_sell_price = the_yield.getNativeSellPrice()
                        stored = pLoopCity.getYieldStored(iYield)
                        if stored == 0 :
                            continue
                        value_per_item=0
                        if ePlayer.isNative() and the_yield.getNativeSellPrice() > 0 :
                            value_per_item=the_price_value*1.0 - native_sell_price / 2.0
                        elif owned:
                            value_per_item = buy_price*1.0
                        if value_per_item==0:
                            continue
                        while stored > 0:
                            this_stack = min(100,stored)
                            stored = stored - this_stack
                            the_yield_values.append( (this_stack,
                                unicode(the_yield.getDescription()),
                                value_per_item,
                                this_stack * value_per_item ,
                                native_sell_price))
                    the_yield_values.sort(key=lambda x: -x[3])
                    value = 0.0
                    value_strength=1.0
                    products=u""
                    comma=u""
                    gold_reserve=0
                    for x in the_yield_values:
                        value += x[3] * value_strength
                        value_strength = value_strength / 2.0
                        gold_reserve += x[0] * x[4]
                        products = products + comma + str(x[0])+u" " + x[1] + " profit:("+str(x[2])+") reserve:" + str(gold_reserve)
                        comma=u","
                    line=u"\t".join((ePlayer.getCivilizationShortDescription(0),
                        pLoopCity.getName(),
                        str(position[0]),
                        str(position[1]),
                        domain,
                        str(cityplot.getArea()),
                        (str(dist).replace(".",",")),
                        nearest_unit_name,
                        str(visited),
                        str(value/((dist*2.0+0.5)**1.15)).replace(".",","),
                        str(gold_reserve).replace(".",","),
                        native_demand_name,
                        str(native_demand_buy_price),
                        str(player_gold),
                        products))
                    print (prefix+u"\t"+line).encode('utf-8')
                    final_result.append(line)
                    (pLoopCity, iter) = ePlayer.nextCity(iter, False)
    for plot in map_to_cover_back:
        plot.setRevealed(0,False,False,-1)
    return final_result