let resize_debouncer
window.onresize = () => {
	clearTimeout(resize_debouncer)
	resize_debouncer = setTimeout(() => {
		get_us_map_data().then(renderMap)
		get_national_treemap_data().then(renderTreeMap)
	}, 100)
}

var NATIONAL_TEXT = 'Total PAC expenditure in each US state'

let NODE_SIZE = 12
let NODE_PADDING = 2
let SCALE = 0.8
let MAX_EXPENDITURE = 1
let FILTER = null

let industries_data_cache = null
const get_industries_data = async () => {
	if (!industries_data_cache) {
		industries_data_cache = await fetch('./industries.json').then((res) =>
			res.json()
		)
	}

	return industries_data_cache
}

let us_map_data_cache = null
const get_us_map_data = async () => {
	if (!us_map_data_cache) {
		us_map_data_cache = await d3.json('./us-counties.topojson')
	}

	return us_map_data_cache
}

let national_treemap_cache = null
const get_national_treemap_data = async () => {
	if (!national_treemap_cache) {
		national_treemap_cache = await fetch(
			'https://pac-finder.ue.r.appspot.com/api/v1/treemap/national'
		).then((res) => res.json())
	}
	return national_treemap_cache
}

let treemap_data_cache = {}
const get_treemap_data = async (id) => {
	if (!(id in treemap_data_cache)) {
		let url = `https://pac-finder.ue.r.appspot.com/api/v1/treemap/state?fips=${id}`
		if (FILTER) {
			url += `&filter=${FILTER}`
		}
		return await fetch(url).then((res) => res.json())
	}

	return treemap_data_cache[id]
}

let expenditure_data_cache = null
const get_expenditure_data = async (id) => {
	if (!expenditure_data_cache) {
		expenditure_data_cache = await fetch(
			`./expenditures.json`
		).then((res) => res.json())
	}

	return expenditure_data_cache
}

let fips_data_cache = null
const get_fips_data = async () => {
	if (!fips_data_cache) {
		fips_data_cache = await fetch(`./fips.json`).then((res) => res.json())
	}

	return fips_data_cache
}

let active,
	path,
	WIDTH,
	MAP_HEIGHT,
	WINDOW_HEIGHT,
	MAP_Y_OFFSET,
	svg,
	map_container,
	map_group,
	pac_group,
	links_group,
	treemap_container,
	state_node_group,
	projection

let state_tooltip = d3
	.select('body')
	.append('div')
	.style('position', 'absolute')
	.style('z-index', '10')
	.style('visibility', 'hidden')
	.style('background', '#ffffff')
	.text('')
	.style('margin-top', '10px')
	.style('margin-left', '10px')
	.style('padding', '10px')
	.style('font-size', '20px')
	.style('border-radius', '4px')
	.style('top', '0px')
	.style('left', '0px')

let info_tooltip = d3
	.select('body')
	.append('div')
	.style('position', 'absolute')
	.style('z-index', '10')
	.style('background', '#ffffff')
	.style('margin-top', '10px')
	.style('margin-left', '10px')
	.style('padding', '10px')
	.style('left', '0px')
	.style('font-size', '20px')
	.style('border-radius', '4px')
	.text(NATIONAL_TEXT)

let dropdown_tooltip = d3
	.select('body')
	.append('div')
	.style('position', 'absolute')
	.style('z-index', '10')
	.style('background', '#ffffff')
	.style('margin-top', '10px')
	.style('margin-right', '10px')
	.style('padding', '10px')
	.style('right', '0px')
	.style('font-size', '20px')
	.style('border-radius', '4px')
	.style('visibility', 'hidden')

let select_element = dropdown_tooltip
	.append('select')
	.on('change', function () {
		FILTER = select_element.node().value
		if (FILTER === 'All Industries') FILTER = null

		const fips_id = parseInt(active.node().id.replace('fips-', ''))
		get_treemap_data(fips_id).then(renderTreeMap)
	})

get_industries_data().then((industries) => {
	for (let industry of industries) {
		select_element
			.append('option')
			.attr('value', industry)
			.style('width', 300)
			.text(industry === 'Unknown' ? 'Misc.' : industry)
	}
})

active = d3.select(null)
const sizeScale = d3
	.scalePow()
	.exponent(0.08)
	.clamp(true)
	.domain([1e-6, 1000000000000])
	.range([0, 1])
	.nice()

async function renderMap(us_map_data) {
	const expenditure_data = await get_expenditure_data()

	WIDTH = window.innerWidth
	WINDOW_HEIGHT = window.innerHeight - 8
	MAP_HEIGHT = Math.floor(window.innerHeight / 2)
	SCALE = WINDOW_HEIGHT / WIDTH > 1.2 ? 0.8 : 0.5
	// MAP_Y_OFFSET = (WINDOW_HEIGHT - MAP_HEIGHT) / 2
	MAP_Y_OFFSET = 0
	info_tooltip.style('top', `${WINDOW_HEIGHT / 2 - 60}px`)
	dropdown_tooltip.style('top', `${WINDOW_HEIGHT / 2 - 60}px`)
	projection = d3
		.geoAlbersUsa()
		.translate([WIDTH / 2, MAP_HEIGHT / 2])
		.scale(WIDTH * SCALE)

	path = d3.geoPath().projection(projection)
	document.getElementById('viz').innerHTML = ''

	svg = d3
		.select('#viz')
		.append('svg')
		.attr('height', WINDOW_HEIGHT)
		.attr('width', WIDTH)

	svg.append('rect')
		.attr('class', 'background')
		.attr('height', WINDOW_HEIGHT)
		.attr('width', WIDTH)
		.on('click', clicked)

	map_container = svg
		.append('svg')
		.attr('width', WIDTH)
		.attr('height', MAP_HEIGHT)
		.attr('y', `${MAP_Y_OFFSET}`)

	map_group = map_container
		.append('g')
		.attr('class', 'us-state')
		.attr('transform', 'translate(0, 0)')
		.attr('width', WIDTH)
		.attr('height', MAP_HEIGHT)

	map_group
		.append('g')
		.attr('id', 'counties')
		.selectAll('path')
		.data(
			topojson.feature(us_map_data, us_map_data.objects.counties).features
		)
		.enter()
		.append('path')

		.attr('fill', function () {
			return d3.schemeSet3[Math.floor(Math.random() * 12)]
		})
		.attr('d', path)
		.attr('class', 'county-boundary')
		.on('click', reset)

	map_group
		.append('g')
		.attr('id', 'states')
		.selectAll('path')
		.data(
			topojson.feature(us_map_data, us_map_data.objects.states).features
		)
		.enter()
		.append('path')
		.attr('d', path)
		.attr('class', 'state')
		.attr('fill', function (d) {
			return d3.interpolatePuBuGn(sizeScale(expenditure_data[d.id]))
		})
		.attr('id', (d) => `fips-${d.id}`)
		.on('click', clicked)

	map_group
		.append('path')
		.datum(
			topojson.mesh(us_map_data, us_map_data.objects.states, function (
				a,
				b
			) {
				return a !== b
			})
		)
		.attr('id', 'state-borders')
		.attr('d', path)
}

function renderTreeMap(data) {
	var root = d3
		.hierarchy(data)
		.sum(function (d) {
			return d.value
		})
		.sort(function (a, b) {
			return a.value - b.value
		})
	d3
		.treemap()
		.size([WIDTH - 10, MAP_HEIGHT - 10])
		.padding(1)(root)

	treemap_container = svg
		.append('svg')
		.attr('width', WIDTH)
		.attr('height', MAP_HEIGHT)
		.attr('x', '5px')
		.attr('y', `${MAP_HEIGHT + 5}px`)

	let tooltip = d3
		.select('body')
		.append('div')
		.style('position', 'absolute')
		.style('z-index', '10')
		.style('visibility', 'hidden')
		.style('background', '#fff')
		.text('a simple tooltip')
		.style('pointer-events', 'none')
		.style('background', '#ffffff')
		.text('')
		.style('padding', '10px')
		.style('font-size', '20px')
		.style('border-radius', '4px')
		.style('top', '0px')
		.style('left', '0px')

	treemap_container
		.selectAll('rect')
		.data(root.leaves())
		.enter()
		.append('rect')
		.attr('x', function (d) {
			return d.x0
		})
		.attr('y', function (d) {
			return d.y0
		})
		.attr('width', function (d) {
			return d.x1 - d.x0
		})
		.attr('height', function (d) {
			return d.y1 - d.y0
		})
		.style('stroke', 'white')
		.style('fill', (d) => {
			return d3.schemeSet3[Math.floor(Math.random() * 12)]
			// return d3.interpolatePuBuGn(sizeScale(d.value))
		})
		.on('mouseover', (d) => {
			tooltip.text(d.data.name)
			tooltip.style('visibility', 'visible')
		})
		.on('mousemove', (d) => {
			tooltip
				.style('top', d.y0 + MAP_HEIGHT + 8 + 'px')
				.style('left', d.x0 + 10 + 'px')
		})
		.on('mouseout', (d) => {
			tooltip.style('visibility', 'hidden')
		})
		.on('click', async (d) => {
			const us_map_data = await get_us_map_data()
			if (d.data.fips) {
				const topo = topojson.feature(
					us_map_data,
					us_map_data.objects.states
				).features
				const found = topo.find((x) => {
					return x.id === parseInt(d.data.fips)
				})

				clicked.bind(
					document.getElementById(`fips-${parseInt(d.data.fips)}`)
				)(found)
			} else {
				console.log(d)
				window.open(
					`https://www.google.com/search?gfns=1&sourceid=navclient&q=${d.data.name}`,

					'_blank'
				)
			}
		})
}

function clicked(d) {
	if (d3.select('.background').node() === this) return reset()
	if (active.node() === this) return reset()

	get_fips_data().then((fips) =>
		info_tooltip.text(`PAC expenditure within ${fips[parseInt(d.id)]}`)
	)

	active.classed('active', false)
	active = d3.select(this).classed('active', true)

	let bounds = path.bounds(d),
		dx = bounds[1][0] - bounds[0][0],
		dy = bounds[1][1] - bounds[0][1],
		x = (bounds[0][0] + bounds[1][0]) / 2,
		y = (bounds[0][1] + bounds[1][1]) / 2,
		scale = 0.9 / Math.max(dx / WIDTH, dy / MAP_HEIGHT),
		translate = [WIDTH / 2 - scale * x, MAP_HEIGHT / 2 - scale * y]

	map_group
		.transition()
		.duration(600)
		.style('stroke-width', 1.5 / scale + 'px')
		.attr('transform', 'translate(' + translate + ')scale(' + scale + ')')

	state_tooltip.style('visibility', 'visible')
	dropdown_tooltip.style('visibility', 'visible')

	get_fips_data().then((fips) => {
		state_tooltip.text(fips[d.id])
	})

	get_treemap_data(d.id).then(renderTreeMap)
}

function reset() {
	active.classed('active', false)
	active = d3.select(null)
	state_tooltip.style('visibility', 'hidden')
	dropdown_tooltip.style('visibility', 'hidden')

	info_tooltip.text(NATIONAL_TEXT)

	get_national_treemap_data().then(renderTreeMap)

	map_group
		.transition()
		.duration(600)
		.style('stroke-width', '1.5px')
		.attr('transform', `translate(0, 0)`)
}

get_us_map_data()
	.then(renderMap)
	.then(get_national_treemap_data)
	.then(renderTreeMap)
