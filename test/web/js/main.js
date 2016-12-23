function toggleFolder(path){
  if($('[class^="'+path+'"]').is(':visible')){
    $('[class^="'+path+'"]').hide()
  } else {
    $('.'+path+'').show()
  }
}
