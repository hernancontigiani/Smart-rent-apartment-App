var url = window.location.origin + window.location.pathname

$(document).ready(function(){
	$('#process').click(function(e)
    {
		// OpenLayer require reload page to show new map
        e.preventDefault();

        clusterAlgorithm = document.getElementById('clusterAlgorithms').value;
        clusters = document.getElementById('clusters').value;
        
        $.post(url, {clusterAlgorithm: clusterAlgorithm, clusters: clusters},
            function(data) {
                $('#result').html('<img src="data:image/png;base64,' + data + '" />');      
                    
            }
        );    


    });
});