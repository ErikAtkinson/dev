/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { getDefaultConfig } from "@web/views/view";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";
import { session } from "@web/session";
import { Domain } from "@web/core/domain";
import { sprintf } from "@web/core/utils/strings";

const { Component, useSubEnv, useState, onMounted, onWillStart, useRef } = owl;
import { loadJS, loadCSS } from "@web/core/assets"

class AgricultureDashboard extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.action = useService("action");
    this.orm = useService("orm");

    this.state = useState({
      agricultureFarms: { 'agriculture_farms': 0 },
      agricultureFarmers: { 'agriculture_farmer': 0 },
      agricultureSeasons: { 'agriculture_season': 0 },
      agricultureCrops: { 'agriculture_crop': 0 },
      agricultureCropProduction: { 'agriculture_crop_production': 0 },
      seasonCropIncidents: { 'season_crop_incident': 0 },
      agricultureResources: { 'agronomists': 0, 'fleets': 0, 'equipments': 0, 'employees': 0, 'animals': 0, 'workers': 0 },
      seasonExpenseReportGraph: { 'name': [], 'labour_charge': [], 'fertiliser_charge': [], 'pesticide_charge': [], 'seed_charge': [], 'equipment_charge': [], 'fleet_charge': [], 'electricity_expense': [] },
      seasonOverallInfo: { 'name': [], 'season_budget': [], 'misc_expense': [], 'production_price': [], 'total_product_income': [] },
      cropIncidentReportGraph: { 'x-axis': [], 'y-axis': [] },
      cropSeasonDurations: { 'data': [] },
      seasonStatusGraph: { 'x-axis': [], 'y-axis': [] },
      cropStockGraph: { 'x-axis': [], 'y-axis': [] },
    });

    useSubEnv({
      config: {
        ...getDefaultConfig(),
        ...this.env.config,
      },
    });

    this.seasonExpenseReportGraph = useRef('season_expense_report');
    this.seasonOverallInfo = useRef('season_overall_info');
    this.cropIncidentReportGraph = useRef('crop_incident_report');
    this.cropSeasonDurations = useRef('crop_season_time_duration');
    this.seasonStatusGraph = useRef('season_status');
    this.cropStockGraph = useRef('crop_stock');

    onWillStart(async () => {
      await loadJS('agriculture_management/static/src/js/lib/xy.js');
      await loadJS('agriculture_management/static/src/js/lib/index.js');
      await loadJS('agriculture_management/static/src/js/lib/Animated.js');
      await loadJS('agriculture_management/static/src/js/lib/percent.js');

      let agricultureData = await this.orm.call('agriculture.dashboard', 'get_agriculture_dashboard', []);
      if (agricultureData) {
        this.state.agricultureFarms = agricultureData;
        this.state.agricultureFarmers = agricultureData;
        this.state.agricultureSeasons = agricultureData;
        this.state.agricultureCrops = agricultureData;
        this.state.agricultureCropProduction = agricultureData;
        this.state.seasonCropIncidents = agricultureData;
        this.state.agricultureResources = agricultureData;
        this.state.seasonExpenseReportGraph = { 'name': agricultureData['season_expense_report'][0], 'labour_charge': agricultureData['season_expense_report'][1], 'fertiliser_charge': agricultureData['season_expense_report'][2], 'pesticide_charge': agricultureData['season_expense_report'][3], 'seed_charge': agricultureData['season_expense_report'][4], 'equipment_charge': agricultureData['season_expense_report'][5], 'fleet_charge': agricultureData['season_expense_report'][6], 'electricity_expense': agricultureData['season_expense_report'][7] };
        this.state.seasonOverallInfo = { 'name': agricultureData['season_overall_info'][0], 'season_budget': agricultureData['season_overall_info'][1], 'misc_expense': agricultureData['season_overall_info'][2], 'production_price': agricultureData['season_overall_info'][3], 'total_product_income': agricultureData['season_overall_info'][4] };
        this.state.cropIncidentReportGraph = { 'x-axis': agricultureData['crop_incident_report'][0], 'y-axis': agricultureData['crop_incident_report'][1] };
        this.state.cropSeasonDurations = { 'data': agricultureData['crop_season_duration'] };
        this.state.seasonStatusGraph = { 'x-axis': agricultureData['season_status'][0], 'y-axis': agricultureData['season_status'][1] };
        this.state.cropStockGraph = { 'x-axis': agricultureData['crop_stock']['crops_name'], 'y-axis': agricultureData['crop_stock']['crop_quantity'] };
      }
    });
    onMounted(() => {
      // this.renderSeasonExpenseReportGraph();
      // this.renderSeasonOverallInfoGraph();
      // this.renderCropIncidentReportGraph();
      // this.renderCropSeasonDurationsGraph();
      // this.renderSeasonStatusGraph(this.seasonStatusGraph.el, this.state.seasonStatusGraph);
      // this.renderCropStockGraph(this.cropStockGraph.el, this.state.cropStockGraph);
    })
  }

  viewAgricultureFarms() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Lands/Farms',
      res_model: 'agriculture.farm',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
      target: 'current',
      context: context,
    });
  }

  viewAgricultureFarmers() {
    let domain = [['is_farmer', '=', true]];
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Farmers',
      res_model: 'res.partner',
      domain: domain,
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
      target: 'current',
      context: context,
    });
  }

  viewAgricultureSeasons() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Seasons',
      res_model: 'agriculture.season',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
      target: 'current',
      context: context,
    });
  }

  viewAgricultureCrops() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Crops',
      res_model: 'agriculture.crop',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity']],
      target: 'current',
      context: context,
    });
  }

  viewAgricultureCropProduction() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Crop Productions',
      res_model: 'crop.production',
      view_mode: 'list',
      views: [[false, 'list'], [false, 'form']],
      target: 'current',
      context: context,
    });
  }

  viewSeasonCropIncidents() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Crop Incidents',
      res_model: 'season.crop.incident',
      view_mode: 'list',
      views: [[false, 'list'], [false, 'form']],
      target: 'current',
      context: context,
    });
  }
  viewAgricultureAgronomists() {
    let domain = [['is_agronomist', '=', true]];
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agronomists',
      res_model: 'res.partner',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
      target: 'current',
      domain: domain,
      context: context,
    });
  }
  viewAgricultureFleets() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Fleets',
      res_model: 'agriculture.fleet',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity'], [false, 'search']],
      target: 'current',
      context: context,
    });
  }
  viewAgricultureEquipments() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Equipments',
      res_model: 'agriculture.equipment',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'search']],
      target: 'current',
      context: context,
    });
  }
  viewAgricultureEmployees() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Employees',
      res_model: 'hr.employee',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity'], [false, 'search']],
      target: 'current',
      context: context,
    });
  }
  viewAgricultureAnimals() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Animals',
      res_model: 'farm.animal',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form']],
      target: 'current',
      context: context,
    });
  }

  viewAgricultureWorkers() {
    let context = { 'create': false }
    this.action.doAction({
      type: 'ir.actions.act_window',
      name: 'Agriculture Workers',
      res_model: 'farm.worker',
      view_mode: 'kanban',
      views: [[false, 'kanban'], [false, 'list'], [false, 'form'], [false, 'activity'], [false, 'search']],
      target: 'current',
      context: context,
    });
  }

  // renderGraph(el, options) {
  //   const graphData = new ApexCharts(el, options);
  //   graphData.render();
  // }

  // renderSeasonExpenseReportGraph() {
  //   const options = {
  //     series: [
  //       {
  //         name: "labour Expenses",
  //         data: this.state.seasonExpenseReportGraph['labour_charge'],
  //       },
  //       {
  //         name: 'Fertiliser Expenses',
  //         data: this.state.seasonExpenseReportGraph['fertiliser_charge'],
  //       },
  //       {
  //         name: "Pesticide Expenses",
  //         data: this.state.seasonExpenseReportGraph['pesticide_charge'],
  //       },
  //       {
  //         name: 'Seed Expenses',
  //         data: this.state.seasonExpenseReportGraph['seed_charge'],
  //       },
  //       {
  //         name: 'Equipment Expenses',
  //         data: this.state.seasonExpenseReportGraph['equipment_charge'],
  //       },
  //       {
  //         name: 'Fleet Expenses',
  //         data: this.state.seasonExpenseReportGraph['fleet_charge'],
  //       },
  //       {
  //         name: 'Electricity Expense',
  //         data: this.state.seasonExpenseReportGraph['electricity_expense'],
  //       },
  //     ],
  //     chart: {
  //       height: 430,
  //       type: 'line',
  //       zoom: {
  //         enabled: false
  //       },
  //     },
  //     colors: ['#e81416','#ffa500','#faeb36','#79c314','#487de7','#4b369d','#70369d'],
  //     dataLabels: {
  //       enabled: false
  //     },
  //     title: {
  //       align: 'left'
  //     },
  //     yaxis: {
  //       title: {
  //         text: 'Amount'
  //       },
  //     },
  //     markers: {
  //       size: 0,
  //       hover: {
  //         sizeOffset: 6
  //       }
  //     },
  //     xaxis: {
  //       categories: this.state.seasonExpenseReportGraph['name'],
  //     },
  //     tooltip: {
  //     },
  //     grid: {
  //       borderColor: '#f1f1f1',
  //     }
  //   };
  //   this.renderGraph(this.seasonExpenseReportGraph.el, options);
  // }

  // renderSeasonOverallInfoGraph() {
  //   const options = {
  //     series: [
  //       {
  //         name: "Season Budget",
  //         data: this.state.seasonOverallInfo['season_budget'],
  //       },
  //       {
  //         name: "Misc Expense",
  //         data: this.state.seasonOverallInfo['misc_expense'],
  //       },
  //       {
  //         name: 'Production Income',
  //         data: this.state.seasonOverallInfo['production_price'],
  //       },
  //       {
  //         name: 'Profit & Loss',
  //         data: this.state.seasonOverallInfo['total_product_income'],
  //       }
  //     ],
  //     chart: {
  //       type: 'bar',
  //       height: 430
  //     },
  //     plotOptions: {
  //       bar: {
  //         horizontal: false,
  //         columnWidth: '30%',
  //         endingShape: 'rounded'
  //       },
  //     },
  //     dataLabels: {
  //       enabled: false
  //     },
  //     stroke: {
  //       show: true,
  //       width: 2,
  //       colors: ['transparent']
  //     },
  //     xaxis: {
  //       categories: this.state.seasonOverallInfo['name'],
  //       title: {
  //         text: 'Season'
  //       }
  //     },
  //     yaxis: {
  //       title: {
  //         text: '(Amount)'
  //       }
  //     },
  //     fill: {
  //       opacity: 1
  //     },
  //     tooltip: {
  //       y: {
  //         formatter: function (val) {
  //           return val + " Amount"
  //         }
  //       }
  //     }
  //   };
  //   this.renderGraph(this.seasonOverallInfo.el, options);
  // }

  // renderCropIncidentReportGraph() {
  //   const options = {
  //     series: [
  //       {
  //         name: "Crop Damage Values",
  //         data: this.state.cropIncidentReportGraph['y-axis'],
  //       },
  //     ],
  //     chart: {
  //       height: 430,
  //       type: 'bar',
  //     },
  //     plotOptions: {
  //       bar: {
  //         columnWidth: '10%',
  //         distributed: true,
  //       }
  //     },
  //     dataLabels: {
  //       enabled: false
  //     },
  //     yaxis: {
  //       title: {
  //         text: 'Estimated Damage Amount'
  //       },
  //     },
  //     legend: {
  //       show: false
  //     },
  //     xaxis: {
  //       categories: this.state.cropIncidentReportGraph['x-axis'],
  //       title: {
  //         text: 'Crop Seasons'
  //       },
  //       labels: {
  //         style: {
  //           fontSize: '15px'
  //         }
  //       }
  //     },
  //   };
  //   this.renderGraph(this.cropIncidentReportGraph.el, options);
  // }

  // renderCropSeasonDurationsGraph() {
  //   let seasons_data = []
  //   let data = this.state.cropSeasonDurations['data']
  //   for (const ss of data) {
  //     seasons_data.push({
  //       'name': ss['name'],
  //       'data': [{
  //         'x': 'Season Duration',
  //         'y': [new Date(ss['start_date']).getTime(), new Date(ss['end_date']).getTime()]
  //       }]
  //     })
  //   }
  //   const options = {
  //     series: seasons_data,
  //     chart: {
  //       height: 430,
  //       type: 'rangeBar',
  //     },
  //     plotOptions: {
  //       bar: {
  //         horizontal: true
  //       }
  //     },
  //     dataLabels: {
  //       enabled: true,
  //       formatter: function (val) {
  //         var a = moment(val[0])
  //         var b = moment(val[1])
  //         var diff = b.diff(a, 'days')
  //         return diff + (diff > 1 ? ' days' : ' day')
  //       }
  //     },
  //     fill: {
  //       type: 'gradient',
  //       gradient: {
  //         shade: 'light',
  //         type: 'vertical',
  //         shadeIntensity: 0.25,
  //         gradientToColors: undefined,
  //         inverseColors: true,
  //         opacityFrom: 1,
  //         opacityTo: 1,
  //         stops: [50, 0, 100, 100]
  //       }
  //     },
  //     yaxis: {
  //          title: {
  //               text: 'Season Duration',
  //           },
  //           labels: {
  //               show: false
  //           }
  //     },
  //     xaxis: {
  //       type: 'datetime',
  //     },
  //     legend: {
  //       position: 'bottom',
  //     }
  //   };
  //   this.renderGraph(this.cropSeasonDurations.el, options);
  // }

  // renderSeasonStatusGraph(div, seasonState) {
  //   const chartData = [];
  //   const root = am5.Root.new(div);

  //   root.setThemes([
  //     am5themes_Animated.new(root)
  //   ]);

  //   const chart = root.container.children.push(am5percent.PieChart.new(root, {
  //     layout: root.verticalLayout,
  //     innerRadius: am5.percent(70),
  //     height: 430
  //   }));

  //   const series = chart.series.push(am5percent.PieSeries.new(root, {
  //     valueField: "value",
  //     categoryField: "category",
  //     alignLabels: false
  //   }));

  //   series.labels.template.setAll({
  //     textType: "circular",
  //     centerX: 0,
  //     centerY: 0
  //   });
  //   series.ticks.template.setAll({
  //     forceHidden: true,
  //   });
  //   series.labels.template.setAll({
  //     forceHidden: true,
  //   });
  //   series.slices.template.setAll({
  //     strokeWidth: 2,
  //     tooltipText:
  //       "{category}: {value}"
  //   });

  //   for (var i = 0; i < seasonState['x-axis'].length; i++) {
  //     chartData.push({
  //       value: seasonState['y-axis'][i],
  //       category: seasonState['x-axis'][i],
  //     });
  //   }
  //   series.data.setAll(chartData);

  //   const legend = chart.children.push(am5.Legend.new(root, {
  //     centerX: am5.percent(50),
  //     x: am5.percent(50),
  //     marginTop: 15,
  //     marginBottom: 15,
  //   }));

  //   legend.data.setAll(series.dataItems);
  //   series.appear(1000, 100);
  // }

  // renderCropStockGraph(div, sessionData) {
  //   const chartData = [];
  //   const root = am5.Root.new(div);
  //   root.setThemes([
  //     am5themes_Animated.new(root)
  //   ]);
  //   const chart = root.container.children.push(am5percent.PieChart.new(root, {
  //     layout: root.verticalLayout
  //   }));
  //   const series = chart.series.push(am5percent.PieSeries.new(root, {
  //     valueField: "value",
  //     categoryField: "category",
  //   }));

  //   series.ticks.template.setAll({
  //     forceHidden: true,
  //   });
  //   series.labels.template.setAll({
  //     forceHidden: true,
  //   });
  //   series.slices.template.setAll({
  //     strokeWidth: 2,
  //     tooltipText:
  //       "{category}: {value}"
  //   });

  //   for (var i = 0; i < sessionData['x-axis'].length; i++) {
  //     chartData.push({
  //       value: sessionData['y-axis'][i],
  //       category: sessionData['x-axis'][i],
  //     });
  //   }
  //   series.data.setAll(chartData);

  //   const legend = chart.children.push(am5.Legend.new(root, {
  //     centerX: am5.percent(50),
  //     x: am5.percent(50),
  //     marginTop: 15,
  //     marginBottom: 15
  //   }));

  //   legend.data.setAll(series.dataItems);
  //   series.appear(1000, 100);
  // }

}
AgricultureDashboard.template = "agriculture_management.agriculture_management_dashboard";
registry.category("actions").add("agriculture_dashboard", AgricultureDashboard);