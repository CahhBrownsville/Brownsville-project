(cluster)  => {
    let reports = 0;
    for(let marker of cluster.getAllChildMarkers()) {
        reports += marker.options.reports
    }

    var c = ' marker-cluster-';
    if (reports < 10) {
        c += 'small';
    } 
    else if (reports < 100) {
        c += 'medium';
    } 
    else {
        c += 'large';
    }

    return L.divIcon({
        html: '<div><span>' + reports + '</span></div>',
        className: 'marker-cluster' + c,
        iconSize: new L.Point(40, 40),
        iconAnchor: [20, 40]
    });
}