Promise.all([
    d3.csv('data/nodes.csv'),
    d3.csv('data/links.csv')
]).then(([nodes, links]) => {
    nodes.forEach(d => {
        d.R = +d.R * 5;
    });

    links.forEach(d => {
        d.id = +d.id;
        d.value = +d.value;
    })

    console.log(nodes);
    console.log(links);

    function createGraph(nodes, edges) {
        const width = 800,
            height = 1000; // SVG的大小
        const margin = {
            // 四周的边距
            top: 30,
            right: 80,
            bottom: 5,
            left: 5,
        };

        const svg = d3
            .select('#showGraph') // 添加SVG
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .call(d3.zoom().scaleExtent([-5, 2]).on('zoom', zoom_action)); // 添加平移和缩放功能

        const content = svg
            .append('g') // 添加一个group包裹svg元素【节点、连边和文本】以进行缩放，目的是为了在缩放时不会影响整个容器的位置
            .attr('class', 'grapgContent')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        content
            .append('defs')
            .append('marker') //三角形【箭头】
            .attr('id', 'arrowhead')
            .attr('viewBox', '-0 -5 10 10')
            .attr('refX', 23) // 标记点的x坐标。如果圆更大，这个也需要更大
            .attr('refY', 0)
            .attr('orient', 'auto')
            .attr('markerWidth', 13)
            .attr('markerHeight', 13)
            .attr('xoverflow', 'visible')
            .append('svg:path')
            .attr('d', 'M 0,-5 L 10 ,0 L 0,5')
            .attr('fill', '#999')
            .style('stroke', 'none');

        var nodeColorScale = d3
            .scaleOrdinal() // 自定义节点的颜色 =d3.scaleOrdinal(d3.schemeSet2)
            .domain([
                'Domain',
                'IP',
                'Cert_SHA256',
                'IP_CIDR',
                'ASN',
                'Whois_Name',
                'Whois_Email',
                'Whois_Phone',
            ])
            .range([
                '#ff9e6d',
                '#86cbff',
                '#c2e5a0',
                '#fff686',
                '#9e79db',
                '#8dd3c7',
                'aquamarine',
                'aqua',
                'crimson',
            ]);

        const linkColorScale = [
            '#ff9e6d',
            '#86cbff',
            '#c2e5a0',
            '#9e79db',
            '#8dd3c7',
            'aquamarine',
            'aqua',
            'crimson',
            '#fff686',
        ];

        /*----------初始化连边------------------------*/

        const link = content
            .selectAll('.links')
            .data(edges)
            .enter()
            .append('line')
            .attr('class', 'links')
            .attr('stroke', (d) => linkColorScale[d.id % linkColorScale.length])
            .attr('stroke-width', '1px')
            .style('opacity', 1)
            .attr('id', (d) => 'line' + d.source + d.target)
            .attr('class', 'links')
            .attr('marker-end', 'url(#arrowhead)');

        const edgepaths = content
            .selectAll('.edgepath') //连边上的标签位置,是的文字按照这个位置进行布局
            .data(edges)
            .enter()
            .append('path')
            .attr('class', 'edgepath')
            .attr('fill-opacity', 0)
            .attr('stroke-opacity', 0)
            .attr('id', function(d, i) {
                return 'edgepath' + i;
            })
            .style('pointer-events', 'none');

        const edgelabels = content
            .selectAll('.edgelabel')
            .data(edges)
            .enter()
            .append('text')
            .style('pointer-events', 'none')
            .attr('class', 'edgelabel')
            .attr('id', function(d, i) {
                return 'edgelabel' + i;
            })
            .attr('font-size', 16)
            .attr('fill', (d) => linkColorScale[d.id % linkColorScale.length]);

        edgelabels
            .append('textPath') //要沿着<path>的形状呈现文本，请将文本包含在<textPath>元素中，该元素具有一个href属性，该属性具有对<path>元素的引用.
            .attr('xlink:href', function(d, i) {
                return '#edgepath' + i;
            })
            .style('text-anchor', 'middle')
            .style('pointer-events', 'none')
            .attr('startOffset', '50%')
            .text((d) => d.value);

        /*----------------------初始化节点-----------------------------*/
        const node = content
            .selectAll('.nodes')
            .data(nodes)
            .enter()
            .append('g')
            .attr('class', 'nodes')
            .call(
                d3
                .drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended)
            );
        node
            .append('circle')
            .attr('r', (d) => d.R) //+ d.runtime/20 )
            .style('stroke', 'grey')
            .style('stroke-opacity', 0.3)
            .style('stroke-width', (d) => d.runtime / 10)
            .style('fill', (d) => nodeColorScale(d.type));

        node
            .append('text')
            .attr('dy', 4)
            .attr('dx', -15)
            .text((d) => d.type);

        /*---------------------定义力导引模型----------------------*/
        var simulation = d3
            .forceSimulation()
            .force(
                'link',
                d3
                .forceLink()
                .id(function(d) {
                    return d.type;
                })
                .distance(200)
            )
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(10));

        simulation.nodes(nodes).on('tick', ticked);

        simulation.force('link').links(edges);
        /*---------------------自定义函数，用于图形缩放和力导引模型-------------*/
        function zoom_action() {
            // 控制图形的平移和缩放
            content.attr('transform', d3.event.transform);
        }

        function ticked() {
            //该函数在每次迭代force算法的时候，更新节点的位置(直接操作节点数据数组)。
            link
                .attr('x1', (d) => d.source.x)
                .attr('y1', (d) => d.source.y)
                .attr('x2', (d) => d.target.x)
                .attr('y2', (d) => d.target.y);

            node.attr('transform', (d) => `translate(${d.x},${d.y})`);
            edgepaths.attr(
                'd',
                (d) =>
                'M ' +
                d.source.x +
                ' ' +
                d.source.y +
                ' L ' +
                d.target.x +
                ' ' +
                d.target.y
            );
        }

        function dragstarted(d) {
            if (!d3.event.active) simulation.alphaTarget(0.3).restart();
            d.fy = d.y;
            d.fx = d.x;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
            if (!d3.event.active) {
                simulation.alphaTarget(0);
            }
            d.fx = null;
            d.fy = null;
        }

        /*添加图例*/

    }
    createGraph(nodes, links);
});